#!/usr/bin/env python3
"""
Minimal ESP32 Ping Test

Simplified test using the fixed ESP32Controller to verify ping works.
"""

from esp32_controller import ESP32Controller
import time

def test_minimal_ping():
    """Test basic ping functionality"""
    print("🔧 Minimal ESP32 Ping Test")
    print("=" * 40)
    
    # Create controller
    controller = ESP32Controller(timeout=10.0)  # Longer timeout for debugging
    
    try:
        # Connect
        if not controller.connect():
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected successfully")
        
        # Wait longer for ESP32 serial system to stabilize
        print("⏰ Waiting 5 seconds for ESP32 to be ready...")
        time.sleep(5)
        
        # Test ping
        print("📤 Sending ping...")
        result = controller.ping()
        
        if result:
            print("✅ Ping successful!")
            return True
        else:
            print("❌ Ping failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    finally:
        controller.disconnect()

if __name__ == "__main__":
    success = test_minimal_ping()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
