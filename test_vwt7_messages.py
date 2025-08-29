#!/usr/bin/env python3
"""
VWT7 CAN Message Test Script

This script connects to the PCAN-USB device and verifies that the ESP32 
CAN simulator generates correct VWT7 messages for:
- Park gear (0x05 in byte 5 of message ID 0x3DC)
- 0 km/h speed (0x0000 in bytes 4-5 of message ID 0x0FD)

Usage:
    python3 test_vwt7_messages.py

Requirements:
    pip3 install python-can
"""

import can
import time
import sys
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class ExpectedMessage:
    """Expected CAN message structure"""
    can_id: int
    dlc: int
    data: List[int]
    description: str

class VWT7MessageTester:
    """Test class for VWT7 CAN message verification"""
    
    def __init__(self, device_path: str = "PCAN_USBBUS1", baudrate: int = 500000):
        self.device_path = device_path
        self.baudrate = baudrate
        self.bus: Optional[can.Bus] = None
        
        # Expected VWT7 messages for Park gear and 0 km/h
        self.expected_messages = {
            0x3DC: ExpectedMessage(
                can_id=0x3DC,
                dlc=8,
                data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00],
                description="VWT7 Gear Message - Park (0x05)"
            ),
            0x0FD: ExpectedMessage(
                can_id=0x0FD,
                dlc=8,
                data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                description="VWT7 Speed Message - 0 km/h"
            )
        }
        
        self.received_messages: Dict[int, can.Message] = {}
        self.test_results: Dict[int, bool] = {}
    
    def connect(self) -> bool:
        """Connect to the PCAN device"""
        try:
            print(f"🔌 Connecting to PCAN device: {self.device_path}")
            print(f"📡 Baudrate: {self.baudrate} bps")
            
            # Create CAN bus interface using PCAN
            self.bus = can.Bus(
                interface='pcan',
                channel=self.device_path,
                bitrate=self.baudrate
            )
            print("✅ Connected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print("\n💡 Troubleshooting:")
            print("   - Make sure PCAN drivers are loaded: lsmod | grep pcan")
            print("   - Check device exists: ls -la /dev/pcan*")
            print("   - Install python-can: pip3 install python-can")
            return False
    
    def disconnect(self):
        """Disconnect from the PCAN device"""
        if self.bus:
            self.bus.shutdown()
            print("🔌 Disconnected from PCAN device")
    
    def listen_for_messages(self, timeout: float = 10.0) -> bool:
        """Listen for CAN messages for a specified timeout period"""
        if not self.bus:
            print("❌ Not connected to bus")
            return False
        
        print(f"\n👂 Listening for VWT7 messages (timeout: {timeout}s)...")
        print("Expected messages:")
        for msg in self.expected_messages.values():
            data_str = ' '.join(f'{b:02X}' for b in msg.data)
            print(f"   ID 0x{msg.can_id:03X}: [{data_str}] - {msg.description}")
        
        start_time = time.time()
        message_count = 0
        
        try:
            while time.time() - start_time < timeout:
                # Receive message with 1 second timeout
                message = self.bus.recv(timeout=1.0)
                
                if message is None:
                    continue
                
                message_count += 1
                self.process_message(message)
                
                # Check if we've received all expected messages
                if len(self.received_messages) >= len(self.expected_messages):
                    print(f"\n✅ Received all expected message types!")
                    break
                    
        except KeyboardInterrupt:
            print(f"\n⏹️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error receiving messages: {e}")
            return False
        
        print(f"\n📊 Summary: Received {message_count} total messages")
        return len(self.received_messages) > 0
    
    def process_message(self, message: can.Message):
        """Process a received CAN message"""
        # Check if this is one of our expected message IDs
        if message.arbitration_id in self.expected_messages:
            self.received_messages[message.arbitration_id] = message
            
            expected = self.expected_messages[message.arbitration_id]
            data_str = ' '.join(f'{b:02X}' for b in message.data)
            
            print(f"\n📨 Received: ID 0x{message.arbitration_id:03X} [{data_str}]")
            print(f"   {expected.description}")
            
            # Verify the message immediately
            self.verify_message(message, expected)
        else:
            # Show other messages too for debugging
            data_str = ' '.join(f'{b:02X}' for b in message.data)
            print(f"📨 Other: ID 0x{message.arbitration_id:03X} [{data_str}]")
    
    def verify_message(self, received: can.Message, expected: ExpectedMessage) -> bool:
        """Verify a received message against expected values"""
        errors = []
        
        # Check DLC
        if received.dlc != expected.dlc:
            errors.append(f"DLC mismatch: expected {expected.dlc}, got {received.dlc}")
        
        # Check data length
        if len(received.data) != len(expected.data):
            errors.append(f"Data length mismatch: expected {len(expected.data)}, got {len(received.data)}")
        else:
            # Check each data byte
            for i, (recv_byte, exp_byte) in enumerate(zip(received.data, expected.data)):
                if recv_byte != exp_byte:
                    errors.append(f"Byte {i}: expected 0x{exp_byte:02X}, got 0x{recv_byte:02X}")
        
        # Store result
        is_valid = len(errors) == 0
        self.test_results[received.arbitration_id] = is_valid
        
        if is_valid:
            print(f"   ✅ PASS - Message format correct!")
        else:
            print(f"   ❌ FAIL - Errors found:")
            for error in errors:
                print(f"      • {error}")
        
        return is_valid
    
    def print_final_results(self):
        """Print final test results"""
        print("\n" + "="*60)
        print("🏁 FINAL TEST RESULTS")
        print("="*60)
        
        total_expected = len(self.expected_messages)
        total_received = len(self.received_messages)
        total_passed = sum(1 for result in self.test_results.values() if result)
        
        print(f"Expected message types: {total_expected}")
        print(f"Received message types: {total_received}")
        print(f"Validation passed: {total_passed}")
        
        for can_id, expected in self.expected_messages.items():
            if can_id in self.received_messages:
                status = "✅ PASS" if self.test_results.get(can_id, False) else "❌ FAIL"
                print(f"  0x{can_id:03X} - {expected.description}: {status}")
            else:
                print(f"  0x{can_id:03X} - {expected.description}: ⚠️  NOT RECEIVED")
        
        if total_received == total_expected and total_passed == total_expected:
            print(f"\n🎉 ALL TESTS PASSED! VWT7 simulator working correctly.")
            return True
        else:
            print(f"\n❌ Some tests failed or messages missing.")
            return False

def main():
    """Main test function"""
    print("🚗 VWT7 CAN Message Tester")
    print("="*50)
    print("Testing ESP32 CAN simulator with VWT7, Park gear, 0 km/h")
    
    # Create tester instance
    tester = VWT7MessageTester()
    
    try:
        # Connect to PCAN device
        if not tester.connect():
            sys.exit(1)
        
        print(f"\n💡 Make sure your ESP32 is:")
        print(f"   - Flashed with the CAN simulator firmware")
        print(f"   - Set to VWT7 vehicle type")
        print(f"   - Set to Park gear and 0 km/h")
        print(f"   - Connected to the CAN bus")
        
        input("\n⏸️  Press Enter when ready to start listening...")
        
        # Listen for messages
        if tester.listen_for_messages(timeout=15.0):
            success = tester.print_final_results()
            sys.exit(0 if success else 1)
        else:
            print("\n❌ No messages received. Check ESP32 connection and setup.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main()
