#!/usr/bin/env python3
"""
VW T6 Implementation Test

Tests the VW T6 message generator implementation with:
- Real VW T6 CAN IDs (0x01A0 for speed, 0x0440 for gear)
- Real VW T6 data format and values
- Verification that T6 is now the default selection
"""

import can
import time
import sys
from esp32_controller import ESP32Controller

def test_vwt6_implementation():
    """Test VW T6 implementation with real CAN IDs and format"""
    print("🚗 VW T6 Implementation Test")
    print("=" * 50)
    
    # Connect to ESP32
    controller = ESP32Controller(timeout=10.0)
    if not controller.connect():
        print("❌ Failed to connect to ESP32")
        return False
    
    print("✅ Connected to ESP32")
    time.sleep(3)  # Wait for ESP32 to stabilize
    
    # Get vehicle info to determine correct baud rate
    initial_status = controller.get_status()
    if not initial_status:
        print("❌ Failed to get ESP32 status")
        controller.disconnect()
        return False
    
    # Map vehicles to their CAN baud rates (from real parser implementation)
    vehicle_baud_rates = {
        'VWT6': 500000,   # 500k
        'VWT7': 500000,   # 500k 
        'VWT5': 500000,   # 500k
        'FORD_CUSTOM': 125000,  # 125k  
        'MB_SPRINTER_2023': 250000,  # 250k
    }
    
    current_vehicle = getattr(initial_status, 'vehicle', None) if hasattr(initial_status, 'vehicle') else initial_status.get('vehicle', 'VWT6')
    can_baud_rate = vehicle_baud_rates.get(current_vehicle, 500000)  # Default to 500k
    
    print(f"🚌 Vehicle: {current_vehicle}, CAN Baud Rate: {can_baud_rate}")
    
    # Connect to CAN bus with correct baud rate
    try:
        can_bus = can.Bus(
            channel="PCAN_USBBUS1", 
            interface="pcan",
            bitrate=can_baud_rate  # ✅ Now matches ESP32!
        )
        print(f"✅ Connected to CAN bus at {can_baud_rate} baud")
    except Exception as e:
        print(f"❌ Failed to connect to CAN: {e}")
        controller.disconnect()
        return False
    
    try:
        # Test 1: Verify T6 is default
        print("\n🧪 Test 1: Verify VW T6 is default vehicle")
        status = controller.get_status()
        if status and hasattr(status, 'vehicle') and status.vehicle == 'VWT6':
            print("✅ VW T6 is correctly set as default vehicle")
        elif status and isinstance(status, dict) and status.get('vehicle') == 'VWT6':
            print("✅ VW T6 is correctly set as default vehicle")
        else:
            vehicle = getattr(status, 'vehicle', None) if status else None
            if not vehicle and isinstance(status, dict):
                vehicle = status.get('vehicle')
            print(f"❌ Default vehicle is {vehicle}, expected VWT6")
            return False
        
        # Test 2: Test T6 Speed Message (50 km/h)
        print("\n🧪 Test 2: Test VW T6 Speed Message (50 km/h)")
        
        # Set speed to 50 km/h
        if not controller.set_speed(50):
            print("❌ Failed to set speed")
            return False
        
        print("📤 Set speed to 50 km/h")
        print("⏰ Waiting 5 seconds for ESP32 to update CAN transmission...")
        time.sleep(5)  # Wait longer for ESP32 to update and transmit new data
        
        # Look for T6 speed message (0x01A0)
        speed_found = False
        for _ in range(30):  # Check for 3 seconds
            message = can_bus.recv(timeout=0.1)
            if message and message.arbitration_id == 0x01A0:
                # T6 speed format: bytes 2-3, little endian, factor 0.005
                speed_raw = message.data[2] | (message.data[3] << 8)
                speed_calculated = speed_raw * 0.005
                
                print(f"📨 T6 Speed Message (0x{message.arbitration_id:03X}): {' '.join(f'{b:02X}' for b in message.data)}")
                print(f"📊 Raw value: {speed_raw}, Calculated speed: {speed_calculated:.1f} km/h")
                
                if abs(speed_calculated - 50.0) < 0.1:  # Within 0.1 km/h
                    print("✅ Speed message correct!")
                    speed_found = True
                else:
                    print(f"❌ Speed mismatch: expected 50.0, got {speed_calculated:.1f}")
                break
        
        if not speed_found:
            print("❌ No T6 speed message received")
            return False
        
        # Test 3: Test T6 Gear Message (Drive)
        print("\n🧪 Test 3: Test VW T6 Gear Message (Drive)")
        
        # Set gear to Drive
        if not controller.set_gear("DRIVE"):
            print("❌ Failed to set gear")
            return False
        
        print("📤 Set gear to DRIVE")
        print("⏰ Waiting 4 seconds for ESP32 to update CAN transmission...")
        time.sleep(4)  # Wait for ESP32 to update and transmit new data
        
        # Look for T6 gear message (0x0440)
        gear_found = False
        for _ in range(30):  # Check for 3 seconds
            message = can_bus.recv(timeout=0.1)
            if message and message.arbitration_id == 0x0440:
                # T6 gear format: byte 1, Drive = 0x50
                gear_raw = message.data[1]
                
                print(f"📨 T6 Gear Message (0x{message.arbitration_id:03X}): {' '.join(f'{b:02X}' for b in message.data)}")
                print(f"📊 Gear byte: 0x{gear_raw:02X}")
                
                if gear_raw == 0x50:  # Real T6 Drive value
                    print("✅ Gear message correct!")
                    gear_found = True
                else:
                    print(f"❌ Gear mismatch: expected 0x50 (Drive), got 0x{gear_raw:02X}")
                break
        
        if not gear_found:
            print("❌ No T6 gear message received")
            return False
        
        # Test 4: Test T6 Park Message
        print("\n🧪 Test 4: Test VW T6 Gear Message (Park)")
        
        # Set gear to Park
        if not controller.set_gear("PARK"):
            print("❌ Failed to set gear to Park")
            return False
        
        print("📤 Set gear to PARK")
        print("⏰ Waiting 4 seconds for ESP32 to update CAN transmission...")
        time.sleep(4)  # Wait for ESP32 to update and transmit new data
        
        # Look for T6 gear message (0x0440) with Park value
        park_found = False
        for _ in range(30):  # Check for 3 seconds
            message = can_bus.recv(timeout=0.1)
            if message and message.arbitration_id == 0x0440:
                # T6 gear format: byte 1, Park = 0x80
                gear_raw = message.data[1]
                
                print(f"📨 T6 Gear Message (0x{message.arbitration_id:03X}): {' '.join(f'{b:02X}' for b in message.data)}")
                print(f"📊 Gear byte: 0x{gear_raw:02X}")
                
                if gear_raw == 0x80:  # Real T6 Park value
                    print("✅ Park gear message correct!")
                    park_found = True
                else:
                    print(f"❌ Park gear mismatch: expected 0x80 (Park), got 0x{gear_raw:02X}")
                break
        
        if not park_found:
            print("❌ No T6 park gear message received")
            return False
        
        # Test 5: Verify CAN baud rate
        print("\n🧪 Test 5: Verify CAN baud rate")
        status = controller.get_status()
        print(f"📊 Current vehicle: {status.get('vehicle')}")
        print("✅ T6 should use 500k baud rate (confirmed by successful CAN communication)")
        
        print("\n🎉 All VW T6 tests PASSED!")
        print("✅ VW T6 is now the default vehicle")
        print("✅ Real T6 CAN IDs and data format working correctly")
        print("✅ Speed messages: 0x01A0 with bytes 2-3, factor 0.005")
        print("✅ Gear messages: 0x0440 with byte 1, real T6 values")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        can_bus.shutdown()
        controller.disconnect()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    success = test_vwt6_implementation()
    sys.exit(0 if success else 1)
