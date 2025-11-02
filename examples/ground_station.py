#!/usr/bin/env python3
"""Example Ground Station receiver (skeleton).

Replace the `receive_lora` stub with your LoRa driver, or adapt to receive
messages forwarded by a gateway.
"""
import json


def receive_lora():
    """Stub: replace with actual LoRa receive. For quick development this can
    read JSON lines from stdin or a socket.
    """
    print('Stub receive: waiting for input (paste JSON line, Ctrl+D to end)')
    try:
        while True:
            line = input()
            if not line:
                continue
            yield line.encode('utf-8')
    except EOFError:
        return


def handle_packet(raw_bytes: bytes):
    try:
        obj = json.loads(raw_bytes.decode('utf-8'))
    except Exception as e:
        print('Failed to decode packet:', e)
        return
    print('Received packet seq:', obj.get('seq'))
    print('  lat,lon,alt:', obj.get('lat'), obj.get('lon'), obj.get('alt'))
    print('  battery (mv):', obj.get('battery_mv'))
    print('  thermal summary:', obj.get('thermal_summary'))


def main():
    for pkt in receive_lora():
        handle_packet(pkt)


if __name__ == '__main__':
    main()
