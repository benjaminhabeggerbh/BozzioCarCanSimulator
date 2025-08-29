#!/usr/bin/env python3
"""
Simple CLI tool to read PEAK CAN dongle at 500k baud

Usage:
    python3 pcan_reader.py                    # Read all messages
    python3 pcan_reader.py --filter 0x1A0    # Filter specific ID
    python3 pcan_reader.py --decode-t6        # Decode VW T6 messages
"""

import can
import time
import argparse
import sys

def decode_vw_t6_message(msg):
    """Decode VW T6 specific messages"""
    if msg.arbitration_id == 0x01A0:  # Speed message
        if len(msg.data) >= 4:
            speed_raw = msg.data[2] | (msg.data[3] << 8)
            speed_kmh = speed_raw * 0.005
            return f"Speed: {speed_kmh:.1f} km/h"
    elif msg.arbitration_id == 0x0440:  # Gear message
        if len(msg.data) >= 2:
            gear_raw = msg.data[1]
            gear_map = {0x80: "PARK", 0x77: "REVERSE", 0x60: "NEUTRAL", 0x50: "DRIVE"}
            gear = gear_map.get(gear_raw, f"UNKNOWN(0x{gear_raw:02X})")
            return f"Gear: {gear}"
    return None

def main():
    parser = argparse.ArgumentParser(description="Read PEAK CAN dongle at 500k baud")
    parser.add_argument("--filter", type=lambda x: int(x, 0), help="Filter specific CAN ID (e.g., 0x1A0)")
    parser.add_argument("--decode-t6", action="store_true", help="Decode VW T6 messages")
    parser.add_argument("--baud", type=int, default=500000, help="CAN baud rate (default: 500000)")
    parser.add_argument("--channel", type=str, default="PCAN_USBBUS1", help="PCAN channel (default: PCAN_USBBUS1)")
    parser.add_argument("--count", type=int, help="Number of messages to capture (default: unlimited)")
    parser.add_argument("--show-ascii", action="store_true", help="Show ASCII representation of data")
    parser.add_argument("--summary", action="store_true", help="Show message summary and analysis")
    args = parser.parse_args()

    print(f"🔌 Connecting to {args.channel} at {args.baud} baud...")
    
    try:
        # Connect to PCAN device
        bus = can.Bus(
            channel=args.channel,
            interface="pcan", 
            bitrate=args.baud
        )
        print(f"✅ Connected successfully!")
        
        if args.filter:
            print(f"🔍 Filtering for CAN ID: 0x{args.filter:03X}")
        if args.decode_t6:
            print("🚗 VW T6 decoding enabled")
        if args.count:
            print(f"📊 Will capture {args.count} messages")
        
        # Print header after connection to avoid bus error interference
        print("")
        print("=" * 90)
        print("📡 CAN MESSAGE CAPTURE")
        print("=" * 90)
        
        header = "Time      | ID    | DLC | Data (all 8 bytes)                     "
        if args.show_ascii:
            header += " | ASCII    "
        if args.decode_t6:
            header += " | Decoded"
        print(header)
        print("-" * len(header))
        
        start_time = time.time()
        message_count = 0
        
        while True:
            try:
                message = bus.recv(timeout=1.0)
                if message is None:
                    continue
                    
                # Filter by ID if specified
                if args.filter and message.arbitration_id != args.filter:
                    continue
                
                message_count += 1
                elapsed = time.time() - start_time
                
                # Format message data - always show 8 bytes, pad with -- for missing bytes
                data_bytes = list(message.data) + [None] * (8 - len(message.data))
                data_str = ' '.join(f'{b:02X}' if b is not None else '--' for b in data_bytes)
                
                # ASCII representation if requested
                ascii_str = ""
                if args.show_ascii:
                    ascii_chars = ''.join(chr(b) if b is not None and 32 <= b <= 126 else '.' for b in data_bytes)
                    ascii_str = f" [{ascii_chars}]"
                
                # Decode if requested
                decoded = ""
                if args.decode_t6:
                    decoded_msg = decode_vw_t6_message(message)
                    if decoded_msg:
                        decoded = f" | {decoded_msg}"
                
                print(f"{elapsed:8.3f}s | 0x{message.arbitration_id:03X} | {message.dlc}   | {data_str:<31}{ascii_str}{decoded}")
                
                # Exit if count reached
                if args.count and message_count >= args.count:
                    break
                    
            except KeyboardInterrupt:
                print(f"\n🛑 Interrupted by user")
                break
            except Exception as e:
                error_msg = str(e)
                if "Bus error" in error_msg:
                    # Bus errors are common and don't need to break the loop
                    continue
                else:
                    print(f"❌ Error receiving message: {e}")
                    break
                
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return 1
    
    finally:
        try:
            bus.shutdown()
            print(f"\n📊 Total messages received: {message_count}")
            
            if args.summary:
                print("\n💡 Message Analysis:")
                print("   • ID 0x001-0x00F: Typically heartbeat/status messages")
                print("   • ID 0x1A0: VW T6 Speed (if data[2:3] ≠ 00)")  
                print("   • ID 0x440: VW T6 Gear (if data[1] = 80/77/60/50)")
                print("   • Small DLC (1-4): Usually status/command messages")
                print("   • All zeros: Device present but no active data")
                
            print("🔌 Disconnected")
        except:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
