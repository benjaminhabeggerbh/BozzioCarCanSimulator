#!/usr/bin/env python3
"""
Simple PCAN connection test

This script tests if we can connect to the PCAN device from Python.
"""

import can
import sys

def test_pcan_connection():
    """Test PCAN device connection"""
    
    # Try different channel formats that PCAN might accept
    channel_formats = [
        'PCAN_USBBUS1',
        'PCAN_USBBUS32', 
        'pcan32',
        '/dev/pcanusb32',
        '/dev/pcan32',
        32
    ]
    
    for channel in channel_formats:
        try:
            print(f"🔧 Testing PCAN device connection...")
            print(f"Channel: {channel}")
            print(f"Baudrate: 500000 bps")
            
            # Try to create bus connection
            bus = can.Bus(
                interface='pcan',
                channel=channel,
                bitrate=500000
            )
            
            print(f"✅ PCAN connection successful with channel: {channel}!")
            
            # Try to receive a message with short timeout
            print("👂 Testing message reception (2s timeout)...")
            message = bus.recv(timeout=2.0)
            
            if message:
                data_str = ' '.join(f'{b:02X}' for b in message.data)
                print(f"📨 Received: ID 0x{message.arbitration_id:03X} [{data_str}]")
            else:
                print("⚠️  No messages received (this is normal if ESP32 isn't sending yet)")
            
            bus.shutdown()
            print("🔌 Connection closed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Channel {channel} failed: {e}")
            continue
    
    print(f"❌ All channel formats failed")
    print("\n💡 Troubleshooting:")
    print("   - Check if PCAN drivers are loaded: lsmod | grep pcan")
    print("   - Check device permissions: ls -la /dev/pcanusb32")
    print("   - Make sure pcanview can connect to the device")
    return False

if __name__ == "__main__":
    success = test_pcan_connection()
    sys.exit(0 if success else 1)
