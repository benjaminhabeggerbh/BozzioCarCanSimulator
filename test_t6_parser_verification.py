#!/usr/bin/env python3
"""
VW T6 Parser Verification Test

This test verifies that our ESP32 T6 generator sends data in exactly
the format the C++ parser expects by:
1. Setting a known speed (100 km/h)
2. Setting a known gear (DRIVE)  
3. Capturing the exact CAN bytes
4. Simulating what the parser would extract
"""

import can
import time
import sys
from esp32_controller import ESP32Controller

def simulate_parser_extraction(can_data, message_type):
    """Simulate what the C++ parser would extract from our CAN data"""
    
    if message_type == "speed":
        # Parser does: tmp = (payload[3] << 8) | payload[2]
        # Then: speed_f = tmp * 0.005
        raw_value = (can_data[3] << 8) | can_data[2]
        speed_kmh = raw_value * 0.005
        return raw_value, speed_kmh
    
    elif message_type == "gear":
        # Parser does: lastGearRawValue = payload[1]
        gear_raw = can_data[1]
        gear_mapping = {
            0x80: "PARK",
            0x77: "REVERSE", 
            0x60: "NEUTRAL",
            0x50: "DRIVE"
        }
        gear_name = gear_mapping.get(gear_raw, f"UNKNOWN(0x{gear_raw:02X})")
        return gear_raw, gear_name

def test_t6_parser_verification():
    """Test T6 parser byte format verification"""
    print("🔬 VW T6 Parser Verification Test")
    print("=" * 60)
    
    # Connect to ESP32
    controller = ESP32Controller(timeout=10.0)
    if not controller.connect():
        print("❌ Failed to connect to ESP32")
        return False
    
    print("✅ Connected to ESP32")
    time.sleep(3)
    
    # Connect to CAN bus
    try:
        can_bus = can.Bus(channel="PCAN_USBBUS1", interface="pcan", bitrate=500000)
        print("✅ Connected to CAN bus at 500k baud")
    except Exception as e:
        print(f"❌ Failed to connect to CAN: {e}")
        controller.disconnect()
        return False
    
    try:
        print("\n🧪 Test 1: Verify 100 km/h Speed Message")
        print("-" * 50)
        
        # Set speed to 100 km/h (easy to verify)
        if not controller.set_speed(100):
            print("❌ Failed to set speed to 100 km/h")
            return False
        
        print("📤 Set speed to 100 km/h")
        print("⏰ Waiting 3 seconds for ESP32 to update...")
        time.sleep(3)
        
        # Capture speed message
        speed_found = False
        for _ in range(30):  # 3 seconds
            message = can_bus.recv(timeout=0.1)
            if message and message.arbitration_id == 0x01A0:
                print(f"📨 Raw CAN: ID=0x{message.arbitration_id:03X}, Data=[{' '.join(f'{b:02X}' for b in message.data)}]")
                
                # Simulate parser extraction
                raw_value, parsed_speed = simulate_parser_extraction(message.data, "speed")
                
                print(f"🧮 Parser calculation:")
                print(f"   raw_value = (data[3] << 8) | data[2] = (0x{message.data[3]:02X} << 8) | 0x{message.data[2]:02X} = {raw_value}")
                print(f"   speed = {raw_value} * 0.005 = {parsed_speed:.1f} km/h")
                
                if abs(parsed_speed - 100.0) < 0.1:
                    print("✅ Speed parser verification PASSED!")
                    speed_found = True
                else:
                    print(f"❌ Speed mismatch: expected 100.0, parser sees {parsed_speed:.1f}")
                break
        
        if not speed_found:
            print("❌ No speed message received")
            return False
        
        print("\n🧪 Test 2: Verify DRIVE Gear Message")
        print("-" * 50)
        
        # Set gear to DRIVE
        if not controller.set_gear("DRIVE"):
            print("❌ Failed to set gear to DRIVE")
            return False
        
        print("📤 Set gear to DRIVE")
        print("⏰ Waiting 3 seconds for ESP32 to update...")
        time.sleep(3)
        
        # Capture gear message
        gear_found = False
        for _ in range(30):  # 3 seconds
            message = can_bus.recv(timeout=0.1)
            if message and message.arbitration_id == 0x0440:
                print(f"📨 Raw CAN: ID=0x{message.arbitration_id:03X}, Data=[{' '.join(f'{b:02X}' for b in message.data)}]")
                
                # Simulate parser extraction
                gear_raw, parsed_gear = simulate_parser_extraction(message.data, "gear")
                
                print(f"🧮 Parser calculation:")
                print(f"   gear_raw = data[1] = 0x{gear_raw:02X}")
                print(f"   gear = {parsed_gear}")
                
                if parsed_gear == "DRIVE":
                    print("✅ Gear parser verification PASSED!")
                    gear_found = True
                else:
                    print(f"❌ Gear mismatch: expected DRIVE, parser sees {parsed_gear}")
                break
        
        if not gear_found:
            print("❌ No gear message received")
            return False
            
        print("\n🎉 All parser verification tests PASSED!")
        print("✅ ESP32 T6 generator data format matches C++ parser expectations")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        can_bus.shutdown()
        controller.disconnect()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    success = test_t6_parser_verification()
    sys.exit(0 if success else 1)
