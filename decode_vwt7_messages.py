#!/usr/bin/env python3
"""
VWT7 CAN Message Decoder

This script listens to VWT7 CAN messages and decodes them to show:
- Current speed in km/h
- Current gear position
- Message timing and counts

Useful for debugging and verifying the ESP32 simulator behavior.
"""

import can
import time
import sys
from typing import Optional, Dict

class VWT7MessageDecoder:
    """Decoder for VWT7 CAN messages"""
    
    def __init__(self, channel: str = "PCAN_USBBUS1", baudrate: int = 500000):
        self.channel = channel
        self.baudrate = baudrate
        self.bus: Optional[can.Bus] = None
        
        # VWT7 message IDs
        self.SPEED_MSG_ID = 0x0FD
        self.GEAR_MSG_ID = 0x3DC
        
        # Gear mapping
        self.gear_map = {
            0x05: "PARK",
            0x04: "REVERSE", 
            0x03: "NEUTRAL",
            0x02: "DRIVE"
        }
        
        # Message counters
        self.message_counts: Dict[int, int] = {}
        self.last_values: Dict[str, any] = {}
    
    def connect(self) -> bool:
        """Connect to the PCAN device"""
        try:
            print(f"🔌 Connecting to PCAN: {self.channel}")
            self.bus = can.Bus(
                interface='pcan',
                channel=self.channel,
                bitrate=self.baudrate
            )
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the PCAN device"""
        if self.bus:
            self.bus.shutdown()
            print("🔌 Disconnected")
    
    def decode_speed_message(self, data: bytes) -> float:
        """Decode VWT7 speed message"""
        if len(data) >= 6:
            # Speed is in bytes 4-5, little endian
            speed_raw = data[4] | (data[5] << 8)
            speed_kmh = speed_raw * 0.01  # VWT7 speed factor
            return speed_kmh
        return 0.0
    
    def decode_gear_message(self, data: bytes) -> str:
        """Decode VWT7 gear message"""
        if len(data) >= 6:
            gear_value = data[5]
            return self.gear_map.get(gear_value, f"UNKNOWN(0x{gear_value:02X})")
        return "UNKNOWN"
    
    def process_message(self, message: can.Message):
        """Process and decode a received message"""
        msg_id = message.arbitration_id
        data = message.data
        
        # Update message count
        self.message_counts[msg_id] = self.message_counts.get(msg_id, 0) + 1
        count = self.message_counts[msg_id]
        
        # Format data
        data_str = ' '.join(f'{b:02X}' for b in data)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        if msg_id == self.SPEED_MSG_ID:
            speed = self.decode_speed_message(data)
            changed = speed != self.last_values.get('speed', None)
            change_indicator = " 🔄" if changed else ""
            print(f"{timestamp} | SPEED  | 0x{msg_id:03X} | {speed:6.1f} km/h | [{data_str}] | #{count}{change_indicator}")
            self.last_values['speed'] = speed
            
        elif msg_id == self.GEAR_MSG_ID:
            gear = self.decode_gear_message(data)
            changed = gear != self.last_values.get('gear', None)
            change_indicator = " 🔄" if changed else ""
            print(f"{timestamp} | GEAR   | 0x{msg_id:03X} | {gear:>8} | [{data_str}] | #{count}{change_indicator}")
            self.last_values['gear'] = gear
            
        else:
            # Show other messages too
            print(f"{timestamp} | OTHER  | 0x{msg_id:03X} | {'':>8} | [{data_str}] | #{count}")
    
    def listen(self, duration: float = None):
        """Listen for messages"""
        if not self.bus:
            print("❌ Not connected")
            return
        
        print(f"\n👂 Listening for VWT7 CAN messages...")
        print(f"Expected IDs: 0x{self.SPEED_MSG_ID:03X} (speed), 0x{self.GEAR_MSG_ID:03X} (gear)")
        print(f"{'Time':8} | {'Type':6} | {'ID':5} | {'Value':8} | {'Data':<23} | Count")
        print("-" * 70)
        
        start_time = time.time()
        
        try:
            while True:
                # Check timeout
                if duration and (time.time() - start_time) > duration:
                    print(f"\n⏰ Timeout reached ({duration}s)")
                    break
                
                # Receive message
                message = self.bus.recv(timeout=1.0)
                if message:
                    self.process_message(message)
                    
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopped by user")
        
        # Print summary
        print(f"\n📊 Message Summary:")
        for msg_id, count in self.message_counts.items():
            if msg_id == self.SPEED_MSG_ID:
                last_speed = self.last_values.get('speed', 'N/A')
                print(f"   0x{msg_id:03X} (SPEED): {count} messages, last value: {last_speed} km/h")
            elif msg_id == self.GEAR_MSG_ID:
                last_gear = self.last_values.get('gear', 'N/A')
                print(f"   0x{msg_id:03X} (GEAR):  {count} messages, last value: {last_gear}")
            else:
                print(f"   0x{msg_id:03X} (OTHER): {count} messages")

def main():
    """Main function"""
    print("🚗 VWT7 CAN Message Decoder")
    print("="*50)
    
    decoder = VWT7MessageDecoder()
    
    try:
        if not decoder.connect():
            sys.exit(1)
        
        print("\n💡 This tool shows real-time VWT7 messages from your ESP32")
        print("Press Ctrl+C to stop")
        
        # Listen indefinitely
        decoder.listen()
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Interrupted by user")
    finally:
        decoder.disconnect()

if __name__ == "__main__":
    main()
