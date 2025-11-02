# Communication & message schema

This document describes the communication channels and a suggested message
schema for sending MAVLink telemetry + thermal data over LoRa.

Channels
- MAVLink: used between flight controller and Raspberry Pi (serial/UART). Use
  a reliable baud rate configured on the FC (commonly 57600 or 115200).
- Thermal sensor: I2C or SPI between sensor and Raspberry Pi.
- LoRa (raw): Raspberry Pi -> Ground station. Use a radio module on both ends
  (SX1276/77/78/79 family or compatible). Do NOT use LoRaWAN for this local
  setup unless you require OTAA/ABP and a network server.

LoRa considerations
- Payload sizing: SX127x supports up to ~255 bytes, but practical payload sizes
  are smaller due to header/CRC and radio settings. Aim for <= 200 bytes per
  packet; split thermal tiles across packets.
- Throughput and airtime: choose Spreading Factor (SF) and Bandwidth with
  range vs throughput trade-off. For long range choose SF10–SF12 but expect
  long airtime and low packet rate.
- Retries: implement application-layer ACKs for critical messages.

Message framing (suggested)
- Use a small binary header + compressed payload to minimize bytes.

Header (fixed 8–12 bytes)
- version (u8)
- seq (u16) — packet sequence number
- flags (u8) — bitmask (e.g., bit0: ACK requested, bit1: more fragments)
- timestamp (u32) — epoch seconds (or relative time)
- payload_type (u8) — 0 = telemetry only, 1 = thermal tile, 2 = telemetry+thermal

Payloads
- Telemetry payload (compact binary)
  - lat (i32) microdegrees
  - lon (i32) microdegrees
  - alt (i16) meters or decimeters
  - heading (u16) centi-degrees
  - groundspeed (u16) cm/s
  - battery_mv (u16)

- Thermal payloads
  - Option A: summary (min/max/mean temps, hot-spot coordinates) — few bytes
  - Option B: compressed tile: small quantized array, compressed with zlib or
    run-length encoding and base64 / raw binary across fragments

Fragmentation
- If a thermal tile exceeds the LoRa MTU, split into numbered fragments and
  reassemble at the ground station using seq+fragment index. Include a
  checksum per fragment and for the complete tile.

Encoding
- Binary (struct) is efficient; use little-endian consistently. For rapid
  development JSON is fine but less bandwidth efficient.

Example JSON (human-friendly, not bandwidth optimized)
{
  "seq":1234,
  "ts":1690000000,
  "lat":51.123456,
  "lon":-0.123456,
  "alt":120.4,
  "battery_mv":11500,
  "thermal_summary": {"min":20.1,"max":42.7}
}

Reliability and ACKs
- Design the ground station to send a short ACK packet (seq + CRC) for
  packets that requested ACK. Use exponential backoff for retransmit.

Security
- Add an HMAC (e.g., HMAC-SHA256 truncated) using a symmetric key provisioned
  on the Pi and ground station to prevent spoofing. Be mindful of payload
  size when adding MACs.
