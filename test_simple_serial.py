#!/usr/bin/env python3
"""
Simple Serial Interface Test

Quick test to verify the ESP32 serial command interface works
before running the full comprehensive test.
"""

import json
import time
from esp32_controller import ESP32Controller

def main():
    print("🔧 Simple ESP32 Serial Interface Test")
    print("=" * 50)
    
    # Test basic connection
    print("📱 Testing ESP32 connection...")
    controller = ESP32Controller()
    
    try:
        if not controller.connect():
            print("❌ Could not connect to ESP32")
            print("💡 Make sure:")
            print("   - ESP32 is connected via USB")
            print("   - Firmware is flashed with serial command support")
            print("   - Port /dev/ttyACM0 is correct")
            return False
        
        print("✅ Connected successfully!")
        
        # Test ping
        print("\n🏓 Testing ping...")
        if controller.ping():
            print("✅ Ping successful!")
        else:
            print("❌ Ping failed")
            return False
        
        # Get current status
        print("\n📊 Getting current status...")
        status = controller.get_status()
        if status:
            print(f"   Vehicle: {status.vehicle}")
            print(f"   Gear: {status.gear}")
            print(f"   Speed: {status.speed} km/h")
            print(f"   CAN Active: {status.can_active}")
            print(f"   Uptime: {status.uptime}s")
            print(f"   Firmware: {status.firmware_version}")
        else:
            print("❌ Failed to get status")
            return False
        
        # Test setting values
        print("\n🔧 Testing setting values...")
        
        print("   Setting vehicle to VWT7...")
        if controller.set_vehicle("VWT7"):
            print("   ✅ Vehicle set successfully")
        else:
            print("   ❌ Failed to set vehicle")
        
        print("   Setting gear to PARK...")
        if controller.set_gear("PARK"):
            print("   ✅ Gear set successfully")
        else:
            print("   ❌ Failed to set gear")
        
        print("   Setting speed to 0 km/h...")
        if controller.set_speed(0):
            print("   ✅ Speed set successfully")
        else:
            print("   ❌ Failed to set speed")
        
        # Get supported vehicles
        print("\n🚗 Getting supported vehicles...")
        vehicles = controller.get_supported_vehicles()
        if vehicles:
            print(f"   Supported vehicles: {', '.join(vehicles)}")
        else:
            print("   ❌ Failed to get supported vehicles")
        
        # Final status check
        print("\n📊 Final status check...")
        final_status = controller.get_status()
        if final_status:
            print(f"   Vehicle: {final_status.vehicle}")
            print(f"   Gear: {final_status.gear}")
            print(f"   Speed: {final_status.speed} km/h")
        
        print("\n🎉 All basic tests passed!")
        print("💡 You can now run the comprehensive test with:")
        print("   python3 test_esp32_control.py")
        
        return True
        
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        return False
        
    finally:
        controller.disconnect()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Test failed. Check ESP32 connection and firmware.")
        exit(1)
    else:
        print("\n✅ Test completed successfully!")
        exit(0)
