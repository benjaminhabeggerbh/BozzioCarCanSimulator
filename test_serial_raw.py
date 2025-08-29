#!/usr/bin/env python3
"""
Raw Serial Communication Test

This test verifies basic serial communication with the ESP32
without JSON parsing to isolate the issue.
"""

import serial
import time
import sys

def test_raw_serial(port="/dev/ttyACM0", baudrate=115200):
    """Test raw serial communication"""
    print("🔧 Raw Serial Communication Test")
    print("=" * 50)
    
    try:
        # Open serial connection
        print(f"🔌 Opening serial port {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for ESP32 to be ready
        
        # Clear any existing data
        ser.flushInput()
        ser.flushOutput()
        
        print("✅ Serial port opened successfully")
        print("📡 Monitoring ESP32 output for 5 seconds...")
        
        # Monitor output for a few seconds
        start_time = time.time()
        received_data = []
        
        while (time.time() - start_time) < 5:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if data.strip():
                    print(f"ESP32: {data.strip()}")
                    received_data.append(data)
        
        if received_data:
            print("✅ ESP32 is sending data via serial")
        else:
            print("⚠️  No data received from ESP32")
        
        # Test sending simple commands
        print("\n📤 Testing simple command sending...")
        
        # Send simple ping
        test_commands = [
            '{"command":"ping"}',
            'ping',
            'hello',
            '{"command":"get_status"}'
        ]
        
        for cmd in test_commands:
            print(f"📤 Sending: {cmd}")
            ser.write((cmd + '\n').encode('utf-8'))
            ser.flush()
            
            # Wait for response
            time.sleep(1)
            response_received = False
            timeout = time.time() + 3
            
            while time.time() < timeout:
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    if response.strip():
                        print(f"📥 Response: {response.strip()}")
                        response_received = True
                        break
                time.sleep(0.1)
            
            if not response_received:
                print("⏰ No response received")
            
            print()
        
        # Close connection
        ser.close()
        print("🔌 Serial connection closed")
        
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("This test helps debug serial communication issues")
    print("Make sure ESP32 is connected and running the latest firmware")
    
    input("\n⏸️  Press Enter to start raw serial test...")
    
    success = test_raw_serial()
    
    if success:
        print("\n✅ Raw serial test completed")
        print("💡 Check the output above to see if ESP32 is responding")
    else:
        print("\n❌ Raw serial test failed")
        print("💡 Check:")
        print("   - ESP32 is connected to /dev/ttyACM0")
        print("   - ESP32 firmware is running")
        print("   - Serial port permissions")

if __name__ == "__main__":
    main()
