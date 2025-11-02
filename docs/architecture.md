# System architecture

This document describes the high-level architecture for the drone telemetry +
thermal data forwarding system.

Components
- Flight controller (FC): runs autopilot firmware (PX4, ArduPilot). Provides
  telemetry over a serial telemetry port (TELEM2) as MAVLink.
- Raspberry Pi (onboard): acts as a companion computer. Responsibilities:
  - Read MAVLink telemetry using DroneKit.py / pymavlink.
  - Read thermal sensor frames (FLIR Lepton, MLX90640) via I2C/SPI.
  - Preprocess and package telemetry + thermal data.
  - Send packets via a LoRa radio module (raw LoRa, not LoRaWAN) to a ground
    station.
- LoRa radio (onboard): SX127x-family or compatible module connected to the Pi
  over SPI.
- Ground station: LoRa gateway/receiver + software to decode messages, display
  telemetry and thermal overlays.

Data flows
1. FC -> Raspberry Pi: MAVLink over serial (UART). The Pi runs DroneKit to
   expose a `Vehicle` object and provides attribute updates (GPS, attitude,
   battery, mode, etc.).
2. Thermal sensor -> Raspberry Pi: sensor frames or low-resolution grid via I2C
   or SPI.
3. Raspberry Pi: periodically (or event-driven) packs a compact payload that
   contains recent telemetry, a small/encoded thermal payload (region of
   interest, statistics or compressed tile), timestamp, and a sequence number.
4. Raspberry Pi -> Ground station: payloads sent over raw LoRa. The ground
   station acknowledges critical packets when necessary.

Sequence (example)
- Onboard:
  1. Read vehicle state from DroneKit (1 Hz or higher).
  2. Acquire a thermal snapshot (or downsampled tile).
  3. Build payload: header (version, seq, timestamp), telemetry fields, and a
     compressed thermal blob or summary.
  4. Transmit via LoRa; wait for ACK if packet marked reliable; otherwise
     continue.
- Ground station:
  1. Receive packet, verify checksum and sequence number.
  2. Send ACK if requested.
  3. Parse telemetry, store, and render thermal overlay in UI.

Design trade-offs
- LoRa is low-bandwidth: send summaries first (GPS, attitude, battery) and
  optionally send thermal tiles across multiple packets with sequencing.
- For critical telemetry (e.g., failsafe or geo-fence events), prefer
  reliability/ACK and repeat, while less-critical thermal imagery can be
  opportunistic.

Security
- Use simple message signing (HMAC) or a lightweight symmetric scheme to avoid
  spoofing. LoRa payloads are sent in clear by default; design for an assumed
  open channel unless encryption is added at application layer.
