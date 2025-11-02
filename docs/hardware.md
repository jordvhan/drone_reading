# Hardware recommendations and wiring notes

Recommended components
- Flight controller: Pixhawk-family (Pixhawk 4, Cube, etc.) running PX4 or
  ArduPilot.
- Raspberry Pi: Pi Zero 2 W (lightweight) or Pi 3/4 for performance. Use the
  Pi that matches your processing and thermal sensor needs.
- LoRa radio module: SX1276/77/78/79 breakout (e.g., RFM95W) or a vendor HAT
  for Raspberry Pi. Make sure the module frequency matches your region (e.g.,
  868 MHz EU, 915 MHz US).
- Thermal sensor: FLIR Lepton (requires breakout like PureThermal) for higher
  resolution or MLX90640 (32x24 thermal array) for direct I2C access.

Wiring overview
- FC <-> Raspberry Pi
  - Use TELEM2 UART on FC to connect to Pi UART (TX/RX cross). Use level
    shifters if the FC uses 5V logic; most FCs use 3.3V and can be connected
    directly to Pi's UART (GPIO14/15).
  - Ensure common ground between Pi and FC.
- Thermal sensor <-> Raspberry Pi
  - MLX90640: I2C (SDA, SCL) + power (3.3V) and ground. Use a breakout and
    ensure correct pull-ups or use Pi's native I2C.
  - FLIR Lepton: SPI or via PureThermal USB breakout.
- LoRa module <-> Raspberry Pi
  - SPI interface (SCK, MOSI, MISO) + NSS (CS), DIO0 (interrupt), RESET.
  - Use a good antenna and keep RF cabling short. Antenna tuning matters.

Power
- Ensure Pi and FC have stable power. If powering Pi from FC's power module
  or BEC, make sure voltage is filtered. Avoid powering Pi from USB battery
  pack that can dip under load.

Mechanical & RF
- Keep LoRa antenna clear of metallic surfaces and move it away from carbon
  fiber and motors when possible.

Regulatory
- Follow local regulations for transmit power and radio bands.
