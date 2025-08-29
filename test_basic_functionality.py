#!/usr/bin/env python3
"""
Basic ESP32 Functionality Test

This test verifies that the ESP32 is working correctly by:
1. Monitoring CAN output to see current messages
2. Providing a simple interface to verify functionality

This doesn't require the serial command interface to work.
"""

import can
import time
import sys
from typing import Dict, List, Optional

class BasicFunctionalityTester:
    """Test basic ESP32 CAN functionality without serial interface"""
    
    def __init__(self, can_channel: str = "PCAN_USBBUS1"):
        self.can_channel = can_channel
        self.can_bus: Optional[can.Bus] = None
        self.received_messages: Dict[int, can.Message] = {}
        
    def connect_can(self) -> bool:
        """Connect to CAN bus"""
        try:
            print(f"🚌 Connecting to CAN bus: {self.can_channel}")
            self.can_bus = can.Bus(
                interface='pcan',
                channel=self.can_channel,
                bitrate=500000
            )
            print("✅ CAN bus connected")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to CAN bus: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from CAN bus"""
        if self.can_bus:
            self.can_bus.shutdown()
            print("🔌 Disconnected from CAN bus")
    
    def listen_for_messages(self, duration: float = 10.0):
        """Listen for CAN messages and analyze them"""
        if not self.can_bus:
            print("❌ CAN bus not connected")
            return False
        
        print(f"\n👂 Listening for CAN messages ({duration}s)...")
        print(f"Expected VWT7 IDs: 0x0FD (speed), 0x3DC (gear)")
        print(f"{'Time':8} | {'ID':5} | {'DLC':3} | {'Data':<23} | Description")
        print("-" * 70)
        
        start_time = time.time()
        message_count = 0
        
        try:
            while (time.time() - start_time) < duration:
                message = self.can_bus.recv(timeout=1.0)
                
                if message:
                    message_count += 1
                    self.analyze_message(message)
                    
        except KeyboardInterrupt:
            print(f"\n⏹️  Interrupted by user")
        
        print(f"\n📊 Summary: Received {message_count} messages")
        self.print_analysis()
        
        return message_count > 0
    
    def analyze_message(self, message: can.Message):
        """Analyze and display a CAN message"""
        msg_id = message.arbitration_id
        data_str = ' '.join(f'{b:02X}' for b in message.data)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Store latest message for each ID
        self.received_messages[msg_id] = message
        
        # Analyze message content
        description = "Unknown"
        if msg_id == 0x0FD:  # VWT7 Speed message
            if len(message.data) >= 6:
                speed_raw = message.data[4] | (message.data[5] << 8)
                speed_kmh = speed_raw * 0.01
                description = f"VWT7 Speed: {speed_kmh:.1f} km/h"
            else:
                description = "VWT7 Speed (invalid length)"
                
        elif msg_id == 0x3DC:  # VWT7 Gear message
            if len(message.data) >= 6:
                gear_value = message.data[5]
                gear_names = {0x05: "PARK", 0x04: "REVERSE", 0x03: "NEUTRAL", 0x02: "DRIVE"}
                gear_name = gear_names.get(gear_value, f"UNKNOWN(0x{gear_value:02X})")
                description = f"VWT7 Gear: {gear_name}"
            else:
                description = "VWT7 Gear (invalid length)"
        
        print(f"{timestamp} | 0x{msg_id:03X} | {message.dlc:3} | {data_str:<23} | {description}")
    
    def print_analysis(self):
        """Print analysis of received messages"""
        print(f"\n🔍 Message Analysis:")
        
        if not self.received_messages:
            print("   ❌ No messages received")
            print("   💡 Check:")
            print("      - ESP32 is powered and running")
            print("      - CAN transceiver is connected")
            print("      - CAN bus wiring is correct")
            return
        
        # Check for expected VWT7 messages
        speed_msg = self.received_messages.get(0x0FD)
        gear_msg = self.received_messages.get(0x3DC)
        
        if speed_msg:
            speed_raw = speed_msg.data[4] | (speed_msg.data[5] << 8)
            speed_kmh = speed_raw * 0.01
            print(f"   ✅ Speed message (0x0FD): {speed_kmh:.1f} km/h")
        else:
            print(f"   ⚠️  No speed message (0x0FD) received")
        
        if gear_msg:
            gear_value = gear_msg.data[5]
            gear_names = {0x05: "PARK", 0x04: "REVERSE", 0x03: "NEUTRAL", 0x02: "DRIVE"}
            gear_name = gear_names.get(gear_value, f"UNKNOWN(0x{gear_value:02X})")
            print(f"   ✅ Gear message (0x3DC): {gear_name}")
        else:
            print(f"   ⚠️  No gear message (0x3DC) received")
        
        # Show all unique message IDs
        unique_ids = sorted(self.received_messages.keys())
        print(f"   📨 Received message IDs: {', '.join(f'0x{msg_id:03X}' for msg_id in unique_ids)}")
        
        # Determine if this looks like VWT7
        if speed_msg and gear_msg:
            print(f"   🎉 ESP32 appears to be working correctly!")
            print(f"   🚗 Vehicle type appears to be: VWT7")
        elif len(unique_ids) > 0:
            print(f"   ⚠️  ESP32 is sending CAN messages but not VWT7 format")
            print(f"   💡 Vehicle might be set to a different type")
        else:
            print(f"   ❌ No recognizable CAN messages detected")

def main():
    print("🔧 ESP32 Basic Functionality Test")
    print("=" * 50)
    print("This test verifies ESP32 CAN functionality without serial commands")
    
    tester = BasicFunctionalityTester()
    
    try:
        if not tester.connect_can():
            print("\n❌ Cannot test without CAN connection")
            print("💡 Make sure:")
            print("   - PEAK CAN device is connected")
            print("   - PEAK drivers are installed")
            print("   - pcanview can see the device")
            return False
        
        print(f"\n💡 Instructions:")
        print(f"   - This test will listen for CAN messages from ESP32")
        print(f"   - Make sure your ESP32 is powered and running")
        print(f"   - Use the ESP32 touch interface to change settings if needed")
        
        input(f"\n⏸️  Press Enter when ready to start listening...")
        
        success = tester.listen_for_messages(15.0)
        
        if success:
            print(f"\n✅ Test completed - ESP32 is transmitting CAN messages!")
            print(f"💡 If you want to control ESP32 via serial:")
            print(f"   1. Make sure the serial interface firmware is working")
            print(f"   2. Try: python3 test_simple_serial.py")
            return True
        else:
            print(f"\n❌ No CAN messages received")
            print(f"💡 Troubleshooting:")
            print(f"   - Check ESP32 power and connections")
            print(f"   - Verify CAN transceiver wiring")
            print(f"   - Check ESP32 is running the CAN simulator firmware")
            return False
    
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
        return False
    
    finally:
        tester.disconnect()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
