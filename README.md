# Davis ISS -> WeeWX with RTL-SDR on Raspberry Pi Model 4B

A working reference configuration for receiving data transmissions from a Davis Instruments Integrated Sensor Suite (ISS) using an RTL-SDR dongle, decoding the packets with `rtldavis`, archiving the observations with WeeWX, and writing one-minute observations to monthly CSV files.

## System overview

```text
Davis ISS
   |
   | 868 MHz (EU configuration)
   v
RTL-SDR dongle
   |
   v
rtldavis
   |
   v
weewx-rtldavis
   |
   v
WeeWX 5.5.0
   +---- SQLite archive: /var/lib/weewx/weewx.sdb
   |
   +---- Monthly CSV: /var/lib/weewx/csv/weather-YYYY-MM.csv
```

## Current working configuration

- Hardware: Raspberry Pi 4 Model B
- OS: Raspberry Pi OS Lite
- WeeWX: 5.5.0
- Python: 3.13.5
- Weather station: Davis ISS
- SDR decoder: [`lheijst/rtldavis`](https://github.com/lheijst/rtldavis)
- WeeWX driver: [`lheijst/weewx-rtldavis`](https://github.com/lheijst/weewx-rtldavis)
- Region: EU
- ISS channel: 1
- Archive interval: 60 seconds
- WeeWX database units: METRICWX
- Database: SQLite
- CSV rotation: one file per calendar month
- CSV timezone: Europe/London

## Repository contents

- [`docs/hardware.md`](docs/hardware.md) - Hardware and station notes
- [`docs/flash_os.md`](docs/flash_os.md) - Flash Raspberry Pi OS Lite (64-bit) to Micro SD Card
- [`docs/raspberry-pi-setup.md`](docs/raspberry-pi-setup.md) - SSH to RPi_4B, configuration and RTC setup
- [`docs/rtldavis-setup.md`](docs/rtldavis-setup.md) - Setup of RTL-SDR Blog Dongle V3 and rtldavis and WeeWX drivers
- [`docs/weewx-setup.md`](docs/weewx-setup.md) - WeeWX configuration and service setup
- [`docs/csv-logging.md`](docs/csv-logging.md) - CSV logger installation and file format
- [`docs/troubleshooting.md`](docs/troubleshooting.md) - common problems encountered during the build
- [`weewx/weewx.conf`](config/weewx.conf.example) - WeeWX example configuration
- [`weewx/csvlogger.py`](weewx/csvlogger.py) - custom WeeWX CSV logging service Python script

## CSV output

Each archive record produces one CSV row. Files are rotated monthly:

```text
weather-2026-09.csv
weather-2026-10.csv
weather-2026-11.csv
```

The CSV uses METRICWX values, ASCII-friendly headers:

```text
dateTime,dateTimeISO,interval,units,outTemp_C,outHumidity_pct,dewpoint_C,heatindex_C,windchill_C,windSpeed_m_per_s,windGust_m_per_s,windDir_deg,windGustDir_deg,windrun_km,rain_mm,rainRate_mm_per_h,radiation_W_per_m2,UV_index
```

## Important configuration note

The live installation changed WeeWX from the default US archive units to METRICWX by setting:

```ini
[StdConvert]
    target_unit = METRICWX
```

This project deliberately does that **before collecting new archive data**. Do not change the target unit on an existing mixed-unit database without following WeeWX's database/unit migration guidance.=

## Acknowledgements

This project builds on WeeWX and the work in `rtldavis` and `weewx-rtldavis` by `lheijst`.

The custom CSV service in this repository is intended to sit alongside those projects; it is independed of and does not replace the SDR decoder or WeeWX archiving.

Thanks also got the ChatGPT which helped a lot with the trouble-shooting as well as the development of the `csvlogger.py` script.
