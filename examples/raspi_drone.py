#!/usr/bin/env python3
"""Example Raspberry Pi agent (skeleton).

This script is a starting point. Replace the LoRa send/receive stubs with
the driver for your LoRa module (e.g., pySX127x or vendor HAT library).
"""
import time
import json
import base64
from dronekit import connect

# Replace with your vehicle connection string, e.g. '/dev/ttyAMA0' or
# 'tcp:127.0.0.1:5760' for SITL
VEHICLE_CONN = '127.0.0.1:14550'

SEQ = 0


def connect_vehicle():
    print('Connecting to vehicle at', VEHICLE_CONN)
    vehicle = connect(VEHICLE_CONN, wait_ready=True)
    return vehicle


def read_thermal_summary():
    """Return a tiny thermal summary. Replace with MLX90640/Lepton read.
    Returns a small dict; for real images, encode/compress bytes and fragment.
    """
    # Placeholder synthetic data
    return {'min': 20.0, 'max': 40.5, 'mean': 28.1}


def send_lora(payload_bytes: bytes):
    """Stub: send bytes via LoRa. Replace with actual radio transmit.
    For development you can write to a local socket or file instead.
    """
    print('--- LoRa SEND ({} bytes) ---'.format(len(payload_bytes)))
    print(payload_bytes)


def build_payload(vehicle, thermal_summary):
    global SEQ
    SEQ += 1
    payload = {
        'seq': SEQ,
        'ts': int(time.time()),
        'lat': vehicle.location.global_frame.lat if vehicle.location else None,
        'lon': vehicle.location.global_frame.lon if vehicle.location else None,
        'alt': vehicle.location.global_frame.alt if vehicle.location else None,
        'heading': vehicle.heading,
        'groundspeed': vehicle.groundspeed,
        'battery_mv': int(vehicle.battery.voltage * 1000) if vehicle.battery else None,
        'thermal_summary': thermal_summary,
    }
    # JSON for readability; consider binary packing for production
    data = json.dumps(payload).encode('utf-8')
    return data


def main():
    vehicle = connect_vehicle()

    try:
        while True:
            thermal = read_thermal_summary()
            payload = build_payload(vehicle, thermal)
            send_lora(payload)
            time.sleep(1)
    except KeyboardInterrupt:
        print('Shutting down')
    finally:
        vehicle.close()


if __name__ == '__main__':
    main()
