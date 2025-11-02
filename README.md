# drone_reading

This repository contains architecture and documentation for a drone system that
captures MAVLink telemetry and thermal sensor data on a Raspberry Pi aboard the
drone and forwards combined payloads to a ground station over raw LoRa radio.

Goals
- Use DroneKit.py / pymavlink on a Raspberry Pi to read MAVLink telemetry from
	a flight controller (Pixhawk or similar).
- Read a thermal sensor (e.g. FLIR Lepton or MLX90640) connected to the Pi.
- Combine telemetry + thermal data and transmit to a ground station using raw
	LoRa (SX127x family) for long-range, low-bandwidth telemetry.

Quickstart
1. Read the docs in `docs/` to choose hardware and configure serial/UART.
2. Install Python dependencies: see `requirements.txt`.
3. Use the example agent in `examples/raspi_drone.py` as a starting point for the
	 Raspberry Pi code; replace the LoRa send/receive stubs with the driver for
	 your LoRa module.
4. Run the ground station example in `examples/ground_station.py` (or your
	 custom UI) to receive and decode messages.

Repository layout
- `docs/` — architecture, communication, hardware, and software design docs.
- `examples/` — skeleton Python agents for Raspberry Pi (drone-side) and ground
	station.
- `requirements.txt` — Python packages used by the examples and recommended for
	the Pi.

Next steps
- Review `docs/communication.md` for the message schema and LoRa tuning notes.
- Pick a LoRa library that matches your radio breakout (e.g. `pySX127x` or a
	vendor-specific driver) and wire up the examples to real hardware.

If you'd like, I can now:
- generate diagrams (PNG/SVG) showing the data flow,
- flesh out the example scripts to work with a specific LoRa module you have,
- or create unit tests and a small local simulator for development.

