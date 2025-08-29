#!/usr/bin/env python3
"""
ESP32 CAN Simulator Control Test

This script tests the complete control flow:
1. Connect to ESP32 via serial
2. Set vehicle type, gear, and speed via JSON commands
3. Verify that CAN messages change accordingly
4. Test GUI updates

Usage:
    python3 test_esp32_control.py

This validates the entire chain: Serial Command -> ESP32 -> GUI Update -> CAN Output
"""

import time
import sys
import can
from typing import Dict, List, Optional
from dataclasses import dataclass

from esp32_controller import ESP32Controller, ESP32Status

@dataclass
class TestCase:
    """A test case with expected CAN messages"""
    name: str
    vehicle: str
    gear: str
    speed: int
    expected_can_ids: List[int]
    expected_gear_value: int
    expected_speed_value: int
    description: str

class ESP32ControlTester:
    """Comprehensive ESP32 control and CAN verification tester"""
    
    def __init__(self, serial_port: str = "/dev/ttyACM0", can_channel: str = "PCAN_USBBUS1"):
        self.serial_port = serial_port
        self.can_channel = can_channel
        
        # Controllers
        self.esp32: Optional[ESP32Controller] = None
        self.can_bus: Optional[can.Bus] = None
        
        # Test tracking
        self.test_results: List[Dict] = []
        self.current_status: Optional[ESP32Status] = None
        
        # Test cases
        self.test_cases = [
            TestCase(
                name="VWT7_Park_0kmh",
                vehicle="VWT7",
                gear="PARK",
                speed=0,
                expected_can_ids=[0x3DC, 0x0FD],
                expected_gear_value=0x05,
                expected_speed_value=0x0000,
                description="VWT7 in Park at 0 km/h"
            ),
            TestCase(
                name="VWT7_Drive_50kmh",
                vehicle="VWT7",
                gear="DRIVE",
                speed=50,
                expected_can_ids=[0x3DC, 0x0FD],
                expected_gear_value=0x02,
                expected_speed_value=5000,  # 50 / 0.01
                description="VWT7 in Drive at 50 km/h"
            ),
            TestCase(
                name="VWT7_Reverse_5kmh",
                vehicle="VWT7",
                gear="REVERSE",
                speed=5,
                expected_can_ids=[0x3DC, 0x0FD],
                expected_gear_value=0x04,
                expected_speed_value=500,  # 5 / 0.01
                description="VWT7 in Reverse at 5 km/h"
            ),
        ]
    
    def setup(self) -> bool:
        """Setup connections to ESP32 and CAN bus"""
        print("🔧 Setting up test environment...")
        
        # Connect to ESP32
        print(f"📱 Connecting to ESP32 on {self.serial_port}...")
        self.esp32 = ESP32Controller(self.serial_port)
        
        # Set up status update callback
        self.esp32.on_status_update = self._on_status_update
        
        if not self.esp32.connect():
            print("❌ Failed to connect to ESP32")
            return False
        
        print("✅ ESP32 connected")
        
        # Connect to CAN bus
        print(f"🚌 Connecting to CAN bus on {self.can_channel}...")
        try:
            self.can_bus = can.Bus(
                interface='pcan',
                channel=self.can_channel,
                bitrate=500000
            )
            print("✅ CAN bus connected")
        except Exception as e:
            print(f"❌ Failed to connect to CAN bus: {e}")
            return False
        
        return True
    
    def cleanup(self):
        """Clean up connections"""
        if self.esp32:
            self.esp32.disconnect()
        
        if self.can_bus:
            self.can_bus.shutdown()
        
        print("🧹 Cleanup completed")
    
    def _on_status_update(self, status: ESP32Status):
        """Callback for ESP32 status updates"""
        self.current_status = status
        print(f"📊 Status Update: {status.vehicle} | {status.gear} | {status.speed} km/h | CAN: {status.can_active}")
    
    def run_test_case(self, test_case: TestCase) -> Dict:
        """Run a single test case"""
        print(f"\n🧪 Running Test: {test_case.name}")
        print(f"📝 {test_case.description}")
        print(f"🎯 Target: {test_case.vehicle}, {test_case.gear}, {test_case.speed} km/h")
        
        result = {
            'name': test_case.name,
            'success': False,
            'errors': [],
            'serial_success': False,
            'gui_update_success': False,
            'can_messages_success': False,
            'received_messages': {}
        }
        
        try:
            # Step 1: Send commands to ESP32
            print(f"📤 Step 1: Sending commands to ESP32...")
            
            commands_success = True
            if not self.esp32.set_vehicle(test_case.vehicle):
                result['errors'].append("Failed to set vehicle")
                commands_success = False
            
            if not self.esp32.set_gear(test_case.gear):
                result['errors'].append("Failed to set gear")
                commands_success = False
            
            if not self.esp32.set_speed(test_case.speed):
                result['errors'].append("Failed to set speed")
                commands_success = False
            
            result['serial_success'] = commands_success
            
            if not commands_success:
                print("❌ Serial commands failed")
                return result
            
            print("✅ Serial commands sent successfully")
            
            # Step 2: Wait for GUI update (status callback)
            print(f"🖥️  Step 2: Waiting for GUI update...")
            
            gui_timeout = 3.0
            start_time = time.time()
            gui_updated = False
            
            while (time.time() - start_time) < gui_timeout:
                if (self.current_status and 
                    self.current_status.vehicle == test_case.vehicle and
                    self.current_status.gear == test_case.gear and
                    self.current_status.speed == test_case.speed):
                    gui_updated = True
                    break
                time.sleep(0.1)
            
            result['gui_update_success'] = gui_updated
            
            if gui_updated:
                print("✅ GUI updated successfully")
            else:
                print("⚠️  GUI update timeout or mismatch")
                if self.current_status:
                    print(f"   Current: {self.current_status.vehicle}, {self.current_status.gear}, {self.current_status.speed}")
                result['errors'].append("GUI update failed or timeout")
            
            # Step 3: Verify CAN messages
            print(f"🚌 Step 3: Checking CAN messages...")
            
            can_success = self._verify_can_messages(test_case, result)
            result['can_messages_success'] = can_success
            
            if can_success:
                print("✅ CAN messages verified")
            else:
                print("❌ CAN message verification failed")
            
            # Overall success
            result['success'] = result['serial_success'] and result['gui_update_success'] and result['can_messages_success']
            
            if result['success']:
                print(f"🎉 Test {test_case.name} PASSED!")
            else:
                print(f"❌ Test {test_case.name} FAILED")
                for error in result['errors']:
                    print(f"   • {error}")
        
        except Exception as e:
            result['errors'].append(f"Test execution error: {e}")
            print(f"💥 Test execution failed: {e}")
        
        return result
    
    def _verify_can_messages(self, test_case: TestCase, result: Dict) -> bool:
        """Verify CAN messages match expected values"""
        received_messages = {}
        
        # Listen for messages for a few seconds
        listen_time = 3.0
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < listen_time:
                message = self.can_bus.recv(timeout=0.5)
                
                if message and message.arbitration_id in test_case.expected_can_ids:
                    received_messages[message.arbitration_id] = message
                    
                    # Stop early if we have all expected messages
                    if len(received_messages) >= len(test_case.expected_can_ids):
                        break
        
        except Exception as e:
            result['errors'].append(f"CAN listening error: {e}")
            return False
        
        result['received_messages'] = {
            hex(msg_id): [f"{b:02X}" for b in msg.data] 
            for msg_id, msg in received_messages.items()
        }
        
        # Verify gear message (0x3DC)
        gear_msg_id = 0x3DC
        if gear_msg_id in received_messages:
            gear_msg = received_messages[gear_msg_id]
            if len(gear_msg.data) >= 6:
                actual_gear = gear_msg.data[5]
                if actual_gear != test_case.expected_gear_value:
                    result['errors'].append(
                        f"Gear mismatch: expected 0x{test_case.expected_gear_value:02X}, got 0x{actual_gear:02X}"
                    )
                    return False
            else:
                result['errors'].append("Gear message too short")
                return False
        else:
            result['errors'].append("Gear message not received")
            return False
        
        # Verify speed message (0x0FD)
        speed_msg_id = 0x0FD
        if speed_msg_id in received_messages:
            speed_msg = received_messages[speed_msg_id]
            if len(speed_msg.data) >= 6:
                actual_speed = speed_msg.data[4] | (speed_msg.data[5] << 8)
                if actual_speed != test_case.expected_speed_value:
                    result['errors'].append(
                        f"Speed mismatch: expected {test_case.expected_speed_value}, got {actual_speed}"
                    )
                    return False
            else:
                result['errors'].append("Speed message too short")
                return False
        else:
            result['errors'].append("Speed message not received")
            return False
        
        return True
    
    def run_all_tests(self) -> bool:
        """Run all test cases"""
        print("🚗 ESP32 CAN Simulator Control Test Suite")
        print("=" * 60)
        
        if not self.setup():
            print("❌ Setup failed")
            return False
        
        try:
            # Get initial status
            print("\n📊 Getting initial ESP32 status...")
            status = self.esp32.get_status()
            if status:
                print(f"Initial state: {status.vehicle} | {status.gear} | {status.speed} km/h")
                self.current_status = status
            
            # Run test cases
            print(f"\n🧪 Running {len(self.test_cases)} test cases...")
            
            for i, test_case in enumerate(self.test_cases, 1):
                print(f"\n📋 Test {i}/{len(self.test_cases)}")
                result = self.run_test_case(test_case)
                self.test_results.append(result)
                
                # Small delay between tests
                time.sleep(1.0)
            
            # Print final results
            self._print_final_results()
            
            # Return overall success
            return all(result['success'] for result in self.test_results)
        
        finally:
            self.cleanup()
    
    def _print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📊 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {result['name']}: {status}")
            
            # Show component results
            serial_status = "✅" if result['serial_success'] else "❌"
            gui_status = "✅" if result['gui_update_success'] else "❌"
            can_status = "✅" if result['can_messages_success'] else "❌"
            
            print(f"    Serial: {serial_status} | GUI: {gui_status} | CAN: {can_status}")
            
            # Show errors
            if result['errors']:
                for error in result['errors']:
                    print(f"    ⚠️  {error}")
            
            # Show received messages
            if result['received_messages']:
                print(f"    📨 CAN Messages:")
                for msg_id, data in result['received_messages'].items():
                    print(f"      {msg_id}: [{' '.join(data)}]")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! ESP32 control system working perfectly!")
        else:
            print(f"\n⚠️  Some tests failed. Check ESP32 serial interface implementation.")

def main():
    """Main test function"""
    tester = ESP32ControlTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        tester.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
