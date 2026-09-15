# Hardware

## Raspberry Pi

- Raspberry Pi 4 Model B
- Raspberry Pi OS Lite
- RTL-SDR USB dongle
- Davis ISS receiver/antenna setup

The exact RTL-SDR model and antenna details should be recorded here if known.

## Davis ISS

The working configuration uses:

- EU frequency configuration
- ISS channel 7
- ISS transmitter configuration as supported by `weewx-rtldavis`

The current ISS installation does not provide barometric pressure to WeeWX. Consequently, `pressure`, `barometer`, and `altimeter` are not populated by the present ISS data stream.

## Future pressure sensor

A future addition is a local I2C pressure sensor connected directly to the Raspberry Pi. That sensor should be integrated into WeeWX as a separate data source rather than modifying `rtldavis`.
