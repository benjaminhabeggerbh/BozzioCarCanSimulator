#!/usr/bin/env python3
"""
Test different baud rates to find what works with your setup
"""

import can
import time

def test_baudrate(baudrate):
    """Test a specific baud rate"""
    print(f"🔧 Testing {baudrate} baud...", end=" ", flush=True)
    
    try:
        bus = can.Bus(
            channel="PCAN_USBBUS1",
            interface="pcan", 
            bitrate=baudrate
        )
        
        # Try to receive a few messages
        error_count = 0
        message_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 2.0:  # Test for 2 seconds
            try:
                message = bus.recv(timeout=0.1)
                if message:
                    message_count += 1
            except Exception as e:
                if "Bus error" in str(e):
                    error_count += 1
                    if error_count > 5:  # Too many errors
                        break
        
        bus.shutdown()
        
        if error_count > 5:
            print(f"❌ Many bus errors ({error_count})")
            return False
        elif message_count > 0:
            print(f"✅ {message_count} messages received, {error_count} errors")
            return True
        else:
            print(f"⚠️  No messages, {error_count} errors") 
            return error_count == 0
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("🔍 Testing PEAK CAN baud rates...")
    print("=" * 50)
    
    # Common CAN baud rates
    baudrates = [125000, 250000, 500000, 1000000]
    
    working_rates = []
    
    for rate in baudrates:
        if test_baudrate(rate):
            working_rates.append(rate)
        time.sleep(0.5)  # Short delay between tests
    
    print("\n📋 Results:")
    if working_rates:
        print(f"✅ Working baud rates: {working_rates}")
        print(f"💡 Recommended: Use {working_rates[0]} baud")
    else:
        print("❌ No baud rates worked reliably")
        print("💡 Check CAN wiring and ESP32 output")

if __name__ == "__main__":
    main()
