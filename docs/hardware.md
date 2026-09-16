# Hardware

## Raspberry Pi

- Raspberry Pi 4 Model B (4G RAM)
- Raspberry Pi OS Lite
- 32G Micro SD Card

An Industrial Grade Micro SD Card is recommended. It is affected less by temperature extremes and does not degrade by constantly writing to it over a long time period.

OS Details:
- Distributor ID:	Debian
- Description:	Debian GNU/Linux 13 (trixie)
- Release:	13
- Codename:	trixie


## Real-Time Clock (RTC)

- Hobby Components DS3231 RTC module for Raspberry Pi
- includes battery


## RTL-SDR USB dongle and antenna

- RTL-SDR Blog V3 R860 RTL2832U 1PPM TCXO SMA Software Defined Radio (Dongle Only) (Black) (USB-C)
- LPRS WR868 Stubby Antenna with SMA Male Connector, ISM Band (RS Stock No.: 703-2978; Mfr. Part No.: WR868; Brand: LPRS)


## Davis ISS

The working configuration uses:

- EU frequency configuration (bought in UK)
- ISS channel 7
- ISS transmitter configuration as supported by `weewx-rtldavis`

The current ISS installation does not provide barometric pressure to WeeWX. Consequently, `pressure`, `barometer`, and `altimeter` are not populated by the present ISS data stream. A future addition is a local I2C pressure sensor connected directly to the Raspberry Pi. That sensor should be integrated into WeeWX as a separate data source rather than modifying `rtldavis`.


## Other useful components

- Ethernet cable for direct communication with laptop (Ubuntu 24.02 LTS)
- Ethernet to USB-C adaptor (StarTech.com, US1GC30W)
- USB-C card reader for flashing the OS onto the Micro SD card