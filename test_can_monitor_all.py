#!/usr/bin/env python3
"""
Monitor ALL CAN Traffic

This test listens to ALL CAN messages to see if the ESP32 
is transmitting anything at all on the CAN bus.
"""

import can
import time
import sys

def monitor_all_can_traffic():
    """Monitor all CAN traffic to diagnose transmission issues"""
    print("🔍 CAN Traffic Monitor - All Messages")
    print("=" * 50)
    
    # Connect to CAN bus with 500k baud rate (VW T6 default)
    try:
        can_bus = can.Bus(
            channel="PCAN_USBBUS1", 
            interface="pcan",
            bitrate=500000
        )
        print(f"✅ Connected to CAN bus at 500k baud")
    except Exception as e:
        print(f"❌ Failed to connect to CAN: {e}")
        return False
    
    try:
        print("👂 Monitoring ALL CAN messages for 30 seconds...")
        print("Time     | ID    | DLC | Data                    | Description")
        print("-" * 70)
        
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < 30:  # Monitor for 30 seconds
            message = can_bus.recv(timeout=0.1)
            if message:
                message_count += 1
                elapsed = time.time() - start_time
                
                # Format message data
                data_str = ' '.join(f'{b:02X}' for b in message.data)
                
                # Identify known message types
                description = ""
                if message.arbitration_id == 0x01A0:
                    description = "VW T6 Speed"
                elif message.arbitration_id == 0x0440:
                    description = "VW T6 Gear"
                elif message.arbitration_id == 0x0FD:
                    description = "VW T7 Speed" 
                elif message.arbitration_id == 0x3DC:
                    description = "VW T7 Gear"
                else:
                    description = "Unknown"
                
                print(f"{elapsed:6.1f}s | 0x{message.arbitration_id:03X} | {message.dlc}   | {data_str:<23} | {description}")
        
        print("-" * 70)
        print(f"📊 Total messages received: {message_count}")
        
        if message_count == 0:
            print("❌ NO CAN messages received!")
            print("💡 This indicates ESP32 CAN transmission is not working")
            print("🔧 Check:")
            print("   - ESP32 CAN wiring") 
            print("   - ESP32 CAN configuration")
            print("   - CAN transceiver power")
            return False
        else:
            print(f"✅ Received {message_count} messages - CAN transmission working!")
            return True
            
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return False
        
    finally:
        can_bus.shutdown()
        print("🔌 Disconnected from CAN bus")

if __name__ == "__main__":
    success = monitor_all_can_traffic()
    sys.exit(0 if success else 1)
