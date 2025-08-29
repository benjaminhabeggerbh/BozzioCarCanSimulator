#!/usr/bin/env python3
"""
Debug Serial Ping Test

Sends a ping command and captures ALL ESP32 output
to debug what's happening with the JSON response.
"""

import serial
import time
import json

def debug_ping_test(port="/dev/ttyACM0", baudrate=115200):
    """Debug ping test with detailed output"""
    print("🔧 Debug Serial Ping Test")
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
        
        # Monitor for a few seconds to establish baseline
        print("📡 Monitoring baseline for 3 seconds...")
        start_time = time.time()
        all_data = []
        
        while (time.time() - start_time) < 3:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if data.strip():
                    print(f"ESP32: {data.strip()}")
                    all_data.append(data)
        
        # Send ping command
        ping_cmd = '{"command":"ping","timestamp":' + str(int(time.time() * 1000)) + '}'
        print(f"\n📤 Sending ping command: {ping_cmd}")
        ser.write((ping_cmd + '\n').encode('utf-8'))
        ser.flush()
        
        # Monitor response for 10 seconds with detailed logging
        print("📥 Monitoring response for 10 seconds...")
        response_start = time.time()
        raw_buffer = ""
        
        while (time.time() - response_start) < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                raw_buffer += data
                
                # Print raw characters for debugging
                for char in data:
                    if char.isprintable() or char in ['\n', '\r', '\t']:
                        print(f"Raw: '{char}' (ord: {ord(char)})", end='')
                        if char == '\n':
                            print(" <NEWLINE>")
                        elif char == '\r':
                            print(" <CARRIAGE_RETURN>")
                        elif char == '\t':
                            print(" <TAB>")
                        else:
                            print()
                    else:
                        print(f"Raw: <non-printable> (ord: {ord(char)})")
        
        print(f"\n📊 Complete raw buffer:")
        print(repr(raw_buffer))
        
        # Try to find JSON patterns
        print(f"\n🔍 Looking for JSON patterns...")
        lines = raw_buffer.split('\n')
        potential_json = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('{') or line.startswith('"type"'):
                print(f"Line {i}: Potential JSON start: {line}")
                potential_json.append(line)
        
        # Try to parse any complete JSON objects
        if '{' in raw_buffer and '}' in raw_buffer:
            json_start = raw_buffer.find('{')
            json_end = raw_buffer.rfind('}')
            if json_start < json_end:
                potential_json_str = raw_buffer[json_start:json_end+1]
                print(f"\n🧪 Attempting to parse JSON:")
                print(repr(potential_json_str))
                
                try:
                    # Clean up whitespace
                    clean_json = ''.join(line.strip() for line in potential_json_str.split('\n'))
                    print(f"Cleaned JSON: {clean_json}")
                    
                    parsed = json.loads(clean_json)
                    print(f"✅ Successfully parsed JSON: {parsed}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
        
        # Close connection
        ser.close()
        print("\n🔌 Serial connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("This test debugs serial communication in detail")
    input("\n⏸️  Press Enter to start debug test...")
    
    debug_ping_test()

if __name__ == "__main__":
    main()
