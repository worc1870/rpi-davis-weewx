# CSV logging

## Purpose

The CSV logger subscribes to WeeWX archive records and appends one row for each archive interval. It does not decode SDR packets and does not query SQLite. WeeWX provides the completed archive record to the service.

## Install

Copy the repository's logger to the WeeWX user module directory:

```bash
sudo cp weewx/csvlogger.py /etc/weewx/bin/user/csvlogger.py
sudo chown root:root /etc/weewx/bin/user/csvlogger.py
sudo chmod 644 /etc/weewx/bin/user/csvlogger.py
```

Create the CSV directory and make it writable by the account running WeeWX. On the documented installation that account is `weewx`:

```bash
sudo mkdir -p /var/lib/weewx/csv
sudo chown -R weewx:weewx /var/lib/weewx/csv
```

## Configuration

Add:

```ini
[CSVLogger]
    filename = /var/lib/weewx/csv/weather-{year}-{month}.csv
    timezone = Europe/London
    decimals = 3
```

and add the service:

```ini
[Engine]
    [[Services]]
        archive_services = weewx.engine.StdArchive, user.csvlogger.CSVLogger
```

Disable the old Cheetah CSV report if present:

```ini
[[CleanCSV]]
    skin = CSV
    enable = false
```

## Monthly rotation

Files are named by local calendar month:

```text
weather-2026-09.csv
weather-2026-10.csv
weather-2026-11.csv
```

An existing monthly file is opened in append mode and is not given a second header after a WeeWX restart.

## Header

The current header is:

```text
dateTime,dateTimeISO,interval,units,outTemp_C,outHumidity_pct,dewpoint_C,heatindex_C,windchill_C,windSpeed_m_per_s,windGust_m_per_s,windDir_deg,windGustDir_deg,windrun_km,rain_mm,rainRate_mm_per_h,radiation_W_per_m2,UV_index
```

The naming convention is deliberately ASCII-friendly and avoids `/` characters while still making units explicit.

## Verify the output

```bash
tail -5 /var/lib/weewx/csv/weather-$(date +%Y-%m).csv
```

A healthy installation should append approximately one row per minute when the Davis ISS stream is healthy.

## Existing file behavior

The logger preserves an existing monthly file and appends to it. If a file was created by an older version of the logger with a different header, the old header remains. The next newly created month will use the current header.
