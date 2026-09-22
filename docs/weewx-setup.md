# WeeWX setup

## Version

The documented installation uses WeeWX 5.5.0 with Python 3.13.5.

## Configure WeeWX

The working configuration as contained in `/etc/weewx/weewx.conf`. Check the following settings.

We added the following `rtldavis` command at the end of `weewx.conf` earlier. Make sure that frequency (`EU`) and ISS channel (`1`) are passed as separate options and not as part of the main command (this is part of the `lheijst` fork changes).

```ini
[Rtldavis]
    cmd = /usr/local/bin/rtldavis -gain 40 -fc 50000
    channel = EU
    iss_channel = 1
    driver = user.rtldavis
```


## Station definition

Change the station type from `Simulator` to `Rtldavis` in `/etc/weewx/weewx.conf`.

```ini
[Station]
    station_type = Rtldavis
```

Also check station name, latitude, longitude and altitude settings in the `[Station]` section.


## METRICWX archive units

Check that units to `METRICWX` under the `[STDConvert]` section to ensure values are saved in `Celsius` `mm`, `m/s` and `hPa`. Setting this to METRIC would mean units such as `Celsius`, `cm`, `km/h` and `hPa`.

```ini
[StdConvert]
    target_unit = METRICWX
```


**Do not change `target_unit` on an existing database casually.** The target unit applies to the values stored by downstream services, so a unit change can create mixed-unit archives if applied to an existing database without migration.


## Archive interval

Set the desired archive interval in seconds. The default is 300 seconds which means WeeWx will create a record every 5 minutes. Here we set it to 60 seconds which is 1 minute.

```ini
[StdArchive]
    archive_interval = 60
```


## SQLite bindings

Leave database settings as they are.

```ini
[DataBindings]
    [[wx_binding]]
        database = archive_sqlite
        table_name = archive
```

```ini
[Databases]
    [[archive_sqlite]]
        database_name = weewx.sdb
        database_type = SQLite
```

```ini
[DatabaseTypes]
    [[SQLite]]
        driver = weedb.sqlite
        SQLITE_ROOT = /var/lib/weewx
```




## CSV service

The CSV logger is installed as a WeeWX service:

```ini
[CSVLogger]
    filename = /var/lib/weewx/csv/weather-{year}-{month}.csv
    timezone = Europe/London
    decimals = 3
```

and included in the service list:

```ini
[Engine]
    [[Services]]
        archive_services = weewx.engine.StdArchive, user.csvlogger.CSVLogger
```



## Verify decoder operation

If needed, check the WeeWX log for lines similar to:
```bash
sudo journalctl -u weewx
```

Check for something like the following. The exact log text may vary by version.
```text
Loading station type Rtldavis (user.rtldavis)
driver version is 0.20
using frequency EU
using iss_channel 1
startup process '/usr/local/bin/rtldavis ...'
```





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

