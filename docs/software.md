# Software architecture and integration notes

Components
- Onboard agent (Raspberry Pi):
  - DroneKit.py / pymavlink listener to receive MAVLink telemetry from FC.
  - Thermal sensor reader (I2C/SPI) to capture or sample the thermal array.
  - Packetizer: builds compact payloads and manages fragmentation/retries.
  - LoRa radio driver: send/receive functions for raw LoRa packets.
  - Supervisor: keeps processes alive, monitors telemetry freshness, and
    handles failsafe behavior.
- Ground station:
  - LoRa radio receiver.
  - Parser and storage (time-series DB or logger).
  - UI to display telemetry and thermal overlays (Web UI or native app).

Process model (onboard)
- Use a small number of processes or threads to keep timing predictable:
  1. MAVLink thread: subscribes to vehicle updates and writes to a thread-safe
     state object.
  2. Sensor thread: reads thermal frames at configured rate, may downsample.
  3. Transmit thread: periodically creates payloads from latest state and
     pushes them to the radio send queue.
  4. Radio thread: handles actual SPI communication and ACK/retries.

Data contracts
- Define a small telemetry struct that covers the fields you need. Keep
  field types compact (integers where possible) to save bytes.

Suggested Python libraries
- dronekit — high-level access to MAVLink vehicle state.
- pymavlink — lower-level MAVLink parsing when you need direct messages.
- smbus2 — I2C communication with thermal sensors (MLX90640).
- numpy — for thermal tile processing.

Testing and simulation
- Use SITL (Software in the Loop) to test DroneKit code without hardware. For
  thermal data, produce a synthetic grid or replay saved frames.

Error-handling and robustness
- Watchdog: if the FC telemetry is lost, mark vehicle as offline and optionally
  send an alert packet via LoRa (short, repeated, request ACK).
- Queueing: avoid blocking the MAVLink thread on radio operations; use a
  non-blocking queue with backpressure.

Deployment notes
- Use systemd (on Linux) or a simple supervisor to run the agent on startup.
- Log to rotating files and expose a small health endpoint (HTTP) for local
  checks.
