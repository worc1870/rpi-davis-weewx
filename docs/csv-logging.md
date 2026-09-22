# CSV logging

## Purpose

The CSV logger is completely separate from WeeWX. It is a Python script that runs as a Linux service. WeeWX provides the completed archive record to the service. It subscribes to WeeWX archive records and appends one row for each archive interval.


## Install

Copy the the Python file `csvlogger.py` to the RPi_4B. 
```bash
scp weewx/csvlogger.py admin@10.42.0.225:
```

On the RPi_4B move it to the WeeWX user module directory and change permissions.

```bash
sudo mv csvlogger.py /etc/weewx/bin/user/csvlogger.py
sudo chown root:root /etc/weewx/bin/user/csvlogger.py
sudo chmod 644 /etc/weewx/bin/user/csvlogger.py
```

Create the CSV directory and make it writable by the account running WeeWX. On the documented installation that account is `weewx`.

```bash
sudo mkdir -p /var/lib/weewx/csv
sudo chown -R weewx:weewx /var/lib/weewx/csv
```


## Configuration

Add the following to `/etc/weewx/weewx.conf` just before the `[Engine]` section. 

Edit the output file name convention, timezone and number of decimals as needed.

```ini
##############################################################################

#   This section adds the CSVLogger.

[CSVLogger]
    filename = /var/lib/weewx/csv/weather-{year}-{month}.csv
    timezone = Europe/London
    decimals = 3
```

Add the CSVLogger service under the `Engine` section.

```ini
[Engine]
    [[Services]]
        archive_services = weewx.engine.StdArchive, user.csvlogger.CSVLogger
```


## Testing the CSVLogger service

Save the `/etc/weewx/weewx.conf` edits. Reboot RPi_4B.
```bash
sudo reboot
```

Test if `rtldavis`, `WeeWX` and `CSVLogger` are all working.
```bash
/usr/local/bin/rtldavis -tf EU -tr 1 -gain 40 -fc 50000   # check that rtldavis is still receiving coded packets from the ISS
sudo systemctl start weewx   # start WeeWX
sudo journalctl -u weewx   # check for error messages
ls -l /var/lib/weewx/csv/   # check the output file was created
cat /var/lib/weewx/csv/weather-YYYY-MM.csv   # check file content
```

Leave WeeWX running for a few minutes. 


## Trouble shooting

```bash
sudo journalctl -u weewx -f
```

Check for something like the following. The exact log text may vary by version.
```text
Loading station type Rtldavis (user.rtldavis)
driver version is 0.20
using frequency EU
using iss_channel 1
startup process '/usr/local/bin/rtldavis ...'
```

NOTE: I ran into an issue with clash between US units METRICWX units which lead to a crash of `rtldavis`. The solution was to remove the initially created database. Once WeeWX starts it will create a new clean one.
```bash
sudo systemctl stop weewx
sudo rm /var/lib/weewx/weewx.sdb
sudo systemctl start weewx
sudo journalctl -u weewx -f   # check for errors
``






## Observations seen in the archive

The working Davis ISS stream populated fields including:

- outTemp
- outHumidity
- dewpoint
- heatindex
- windchill
- windSpeed
- windGust
- windDir
- windGustDir
- windrun
- rain
- rainRate
- radiation
- UV

The current setup did not populate `pressure`, `barometer`, `altimeter`, or `rxCheckPercent` in the tested archive records.
















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
