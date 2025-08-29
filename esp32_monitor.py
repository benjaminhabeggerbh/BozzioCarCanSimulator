#!/usr/bin/env python3
"""
ESP32 Serial Monitor

Simple monitor to see what the ESP32 is outputting over serial.
Useful for debugging the serial command interface.
"""

import serial
import time
import json
import sys

def monitor_esp32(port="/dev/ttyACM0", baudrate=115200):
    """Monitor ESP32 serial output"""
    
    print(f"🔍 ESP32 Serial Monitor")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        # Open serial connection
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for connection
        
        print("📡 Connected! Monitoring output...")
        print("-" * 50)
        
        while True:
            try:
                # Read line
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        timestamp = time.strftime("%H:%M:%S")
                        
                        # Try to parse as JSON for pretty printing
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                json_data = json.loads(line)
                                print(f"[{timestamp}] JSON: {json.dumps(json_data, indent=2)}")
                            except json.JSONDecodeError:
                                print(f"[{timestamp}] RAW: {line}")
                        else:
                            print(f"[{timestamp}] LOG: {line}")
                
                time.sleep(0.01)  # Small delay
                
            except serial.SerialException:
                print("❌ Serial connection lost")
                break
                
    except serial.SerialException as e:
        print(f"❌ Failed to connect to {port}: {e}")
        print("💡 Make sure:")
        print("   - ESP32 is connected via USB")
        print("   - Port is correct (check with 'ls /dev/tty*')")
        print("   - No other programs are using the port")
        return False
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Monitoring stopped by user")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
    
    return True

def send_test_command(port="/dev/ttyACM0", baudrate=115200):
    """Send a test command to ESP32"""
    
    print(f"📤 Sending test command...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=5)
        time.sleep(2)  # Wait for connection
        
        # Send ping command
        command = {"command": "ping", "timestamp": int(time.time() * 1000)}
        command_json = json.dumps(command) + '\n'
        
        print(f"Sending: {command}")
        ser.write(command_json.encode('utf-8'))
        ser.flush()
        
        # Wait for response
        start_time = time.time()
        while (time.time() - start_time) < 5:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"Response: {response}")
                    try:
                        json_response = json.loads(response)
                        if json_response.get('command') == 'ping':
                            print("✅ Ping successful!")
                            return True
                    except json.JSONDecodeError:
                        pass
            time.sleep(0.1)
        
        print("⏰ No response received")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            send_test_command()
        elif sys.argv[1] == "monitor":
            monitor_esp32()
        else:
            print("Usage: python3 esp32_monitor.py [monitor|test]")
    else:
        # Default: monitor
        monitor_esp32()

if __name__ == "__main__":
    main()
