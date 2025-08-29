#!/usr/bin/env python3
"""
ESP32 CAN Simulator Controller

This module provides a Python interface to control the ESP32 CAN simulator
via serial communication using JSON commands. It supports setting vehicle type,
gear, speed, and retrieving status information.

Future: Can be extended to support WiFi communication.

Usage:
    controller = ESP32Controller("/dev/ttyACM0")
    controller.connect()
    controller.set_vehicle("VWT7")
    controller.set_gear("PARK")
    controller.set_speed(120)
    status = controller.get_status()
"""

import serial
import json
import time
import threading
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass

class VehicleType(Enum):
    """Supported vehicle types"""
    VWT7 = "VWT7"
    VWT6 = "VWT6"
    VW_T5 = "VWT5"
    MERCEDES_SPRINTER = "MERCEDES_SPRINTER"
    JEEP_RENEGADE = "JEEP_RENEGADE"

class Gear(Enum):
    """Supported gear positions"""
    PARK = "PARK"
    REVERSE = "REVERSE"
    NEUTRAL = "NEUTRAL"
    DRIVE = "DRIVE"

@dataclass
class ESP32Status:
    """Current ESP32 simulator status"""
    vehicle: str
    gear: str
    speed: int
    can_active: bool
    uptime: int
    firmware_version: str = "unknown"

class ESP32Controller:
    """Serial controller for ESP32 CAN simulator"""
    
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 115200, timeout: float = 5.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        
        # Response handling
        self._response_callbacks: Dict[str, Callable] = {}
        self._command_responses: Dict[str, Dict] = {}
        self._response_timeout = 5.0
        
        # Background reading
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Event callbacks
        self.on_status_update: Optional[Callable[[ESP32Status], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
    def connect(self) -> bool:
        """Connect to ESP32 via serial"""
        try:
            print(f"🔌 Connecting to ESP32 on {self.port} at {self.baudrate} baud...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                write_timeout=self.timeout
            )
            
            # Wait for ESP32 to boot up
            time.sleep(2.0)
            
            # Clear any pending data
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            # Start background reading thread
            self._running = True
            self._read_thread = threading.Thread(target=self._read_responses, daemon=True)
            self._read_thread.start()
# print(f"📡 Background reader thread started")  # Debug disabled
            
            # Connection established - skip ping test for now
            print("✅ Connected to ESP32 successfully!")
            return True
                
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            if self.serial:
                self.serial.close()
                self.serial = None
            return False
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self._running = False
        
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=1.0)
        
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("🔌 Disconnected from ESP32")
        
        self.serial = None
    
    def _read_responses(self):
        """Background thread to read responses from ESP32"""
        import re
        buffer = ""
        
# print(f"📡 Reader thread starting...")  # Debug disabled
        
        while self._running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                    # print(f"📨 Received {len(data)} bytes: {repr(data[:100])}")  # Debug disabled
                    
                    # Remove ANSI color codes
                    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
                    clean_data = ansi_escape.sub('', data)
                    # print(f"🧹 Clean data: {repr(clean_data[:100])}")  # Debug disabled
                    
                    buffer += clean_data
                    
                    # Look for complete JSON objects using brace matching
                    while buffer:
                        # Find start of JSON
                        json_start = buffer.find('{')
                        if json_start == -1:
                            # No JSON start, process any lines and clear buffer
                            lines = buffer.split('\n')
                            for line in lines[:-1]:  # Process all complete lines
                                line = line.strip()
                                if line and not line.startswith('{'):
                                    # Print ALL debug lines to see if SerialCmd is working
                                    print(f"ESP32: {line}")
                            buffer = lines[-1]  # Keep incomplete line
                            break
                        
                        # Handle any text before JSON
                        if json_start > 0:
                            pre_json = buffer[:json_start]
                            lines = pre_json.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('{'):
                                    # Print ALL debug lines to see if SerialCmd is working
                                    print(f"ESP32: {line}")
                            buffer = buffer[json_start:]
                        
                        # Find matching closing brace
                        brace_count = 0
                        json_end = -1
                        for i, char in enumerate(buffer):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i
                                    break
                        
                        if json_end == -1:
                            # Incomplete JSON, wait for more data
                            break
                        
                        # Extract and process complete JSON
                        json_str = buffer[:json_end + 1]
                        buffer = buffer[json_end + 1:]
                        
                        # Clean up multiline JSON formatting and whitespace
                        clean_json = ''.join(line.strip() for line in json_str.split('\n'))
                        
                        # Debug output (disabled for cleaner interface)
                        # print(f"🔍 Found JSON: {clean_json}")
                        
                        # Skip if this is our own command echo
                        if '"command"' in clean_json and '"timestamp"' in clean_json and '"type"' not in clean_json:
                            # print(f"📤 Skipping command echo")
                            continue  # This is the command we sent, not a response
                        
                        # print(f"📥 Processing response: {clean_json}")
                        self._process_response(clean_json)
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self._running:  # Only log errors if we're supposed to be running
                    print(f"⚠️  Error reading from ESP32: {e}")
                break
    
    def _process_response(self, line: str):
        """Process a response line from ESP32"""
        try:
            # print(f"🧮 Processing line: {repr(line)}")  # Debug disabled
            # Try to parse as JSON
            if line.startswith('{') and line.endswith('}'):
                response = json.loads(line)
                # print(f"✅ Parsed JSON: {response}")  # Debug disabled
                self._handle_json_response(response)
            else:
                # Handle non-JSON responses (debug output, etc.)
                print(f"ESP32: {line}")
                
        except json.JSONDecodeError as e:
            # Non-JSON line (probably debug output)
            print(f"❌ JSON decode error: {e}")
            print(f"ESP32: {line}")
        except Exception as e:
            print(f"⚠️  Error processing response: {e}")
    
    def _handle_json_response(self, response: Dict[str, Any]):
        """Handle a JSON response from ESP32"""
        response_type = response.get('type', 'unknown')
        command = response.get('command', '')
        
        # print(f"🎯 Handling JSON response: type={response_type}, command={command}")  # Debug disabled
        
        if response_type == 'response':
            # Command response
            # print(f"💾 Storing response for command '{command}': {response}")  # Debug disabled  
            self._command_responses[command] = response
            
        elif response_type == 'status_update':
            # Status update notification
            if self.on_status_update:
                status = ESP32Status(
                    vehicle=response.get('vehicle', 'unknown'),
                    gear=response.get('gear', 'unknown'),
                    speed=response.get('speed', 0),
                    can_active=response.get('can_active', False),
                    uptime=response.get('uptime', 0),
                    firmware_version=response.get('firmware_version', 'unknown')
                )
                self.on_status_update(status)
                
        elif response_type == 'error':
            # Error notification
            error_msg = response.get('message', 'Unknown error')
            print(f"❌ ESP32 Error: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
        
        # Debug: print all responses
        print(f"📨 ESP32 Response: {response}")
    
    def _send_command_sync(self, command: str, **kwargs) -> Optional[Dict]:
        """Send command and wait for response"""
        if not self.serial or not self.serial.is_open:
            print("❌ Not connected to ESP32")
            return None
        
        # Build command
        cmd_dict = {
            "command": command,
            "timestamp": int(time.time() * 1000)
        }
        cmd_dict.update(kwargs)
        
        # Clear any previous response
        if command in self._command_responses:
            del self._command_responses[command]
        
        try:
            # Send command
            cmd_json = json.dumps(cmd_dict) + '\r\n'  # Use CRLF for ESP32
            print(f"📤 Sending: {cmd_dict}")
            print(f"📤 Raw command: {repr(cmd_json)}")
            self.serial.write(cmd_json.encode('utf-8'))
            self.serial.flush()
            print(f"📤 Command sent successfully")
            
            # Wait for response
            timeout = kwargs.get('timeout', self._response_timeout)
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if command in self._command_responses:
                    response = self._command_responses[command]
                    del self._command_responses[command]  # Clean up
                    return response
                time.sleep(0.01)
            
            print(f"⏰ Timeout waiting for response to '{command}'")
            return None
            
        except Exception as e:
            print(f"❌ Error sending command '{command}': {e}")
            return None
    
    # === High-level API methods ===
    
    def ping(self) -> bool:
        """Test ESP32 connection"""
        response = self._send_command_sync("ping")
        return response is not None and response.get('status') == 'ok'
    
    def get_status(self) -> Optional[ESP32Status]:
        """Get current ESP32 status"""
        response = self._send_command_sync("get_status")
        if response and response.get('status') == 'ok':
            return ESP32Status(
                vehicle=response.get('vehicle', 'unknown'),
                gear=response.get('gear', 'unknown'),
                speed=response.get('speed', 0),
                can_active=response.get('can_active', False),
                uptime=response.get('uptime', 0),
                firmware_version=response.get('firmware_version', 'unknown')
            )
        return None
    
    def set_vehicle(self, vehicle: str) -> bool:
        """Set vehicle type"""
        response = self._send_command_sync("set_vehicle", vehicle=vehicle)
        return response is not None and response.get('status') == 'ok'
    
    def set_gear(self, gear: str) -> bool:
        """Set gear position"""
        response = self._send_command_sync("set_gear", gear=gear)
        return response is not None and response.get('status') == 'ok'
    
    def set_speed(self, speed: int) -> bool:
        """Set speed in km/h"""
        response = self._send_command_sync("set_speed", speed=speed)
        return response is not None and response.get('status') == 'ok'
    
    def set_can_active(self, active: bool) -> bool:
        """Enable/disable CAN transmission"""
        response = self._send_command_sync("set_can_active", active=active)
        return response is not None and response.get('status') == 'ok'
    
    def get_supported_vehicles(self) -> Optional[list]:
        """Get list of supported vehicles"""
        response = self._send_command_sync("get_supported_vehicles")
        if response and response.get('status') == 'ok':
            return response.get('vehicles', [])
        return None
    
    def reset_settings(self) -> bool:
        """Reset ESP32 to default settings"""
        response = self._send_command_sync("reset_settings")
        return response is not None and response.get('status') == 'ok'
    
    def __enter__(self):
        """Context manager entry"""
        if self.connect():
            return self
        else:
            raise ConnectionError("Failed to connect to ESP32")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# === Convenience functions ===

def create_controller(port: str = "/dev/ttyACM0") -> ESP32Controller:
    """Create and return an ESP32Controller instance"""
    return ESP32Controller(port)

def test_connection(port: str = "/dev/ttyACM0") -> bool:
    """Test if ESP32 is responding on the given port"""
    try:
        with ESP32Controller(port) as controller:
            return controller.ping()
    except:
        return False

if __name__ == "__main__":
    # Simple test/demo
    print("🚗 ESP32 Controller Test")
    print("=" * 50)
    
    controller = ESP32Controller()
    
    try:
        if controller.connect():
            print("\n📊 Testing basic commands...")
            
            # Get status
            status = controller.get_status()
            if status:
                print(f"Current vehicle: {status.vehicle}")
                print(f"Current gear: {status.gear}")
                print(f"Current speed: {status.speed} km/h")
                print(f"CAN active: {status.can_active}")
            
            # Test setting values
            print(f"\n🔧 Testing set commands...")
            controller.set_vehicle("VWT7")
            controller.set_gear("PARK")
            controller.set_speed(0)
            
            print("✅ Basic test completed")
        else:
            print("❌ Failed to connect")
            
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    finally:
        controller.disconnect()
