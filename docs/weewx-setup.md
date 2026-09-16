# WeeWX setup

## Version

The documented installation uses WeeWX 5.5.0 with Python 3.13.5.

## Station definition

The live station uses:

```ini
[Station]
    station_type = Rtldavis
```

The live configuration also contains the station's location, altitude, and other private/site-specific values. Do not publish those values unless you are happy for them to be public.

## METRICWX archive units

The working database was created with:

```ini
[StdConvert]
    target_unit = METRICWX
```

The result was verified in SQLite with `usUnits = 17` and values consistent with METRICWX, such as degrees Celsius for temperature and metres per second for wind speed.

**Do not change `target_unit` on an existing database casually.** The target unit applies to the values stored by downstream services, so a unit change can create mixed-unit archives if applied to an existing database without migration.

## Archive interval

The working configuration uses:

```ini
[StdArchive]
    archive_interval = 60
    record_generation = hardware
```

The resulting archive timestamps were exactly one minute apart.

## SQLite binding

The archive uses:

```ini
[DataBindings]
    [[wx_binding]]
        database = archive_sqlite
        table_name = archive
```

and:

```ini
[Databases]
    [[archive_sqlite]]
        database_name = weewx.sdb
        database_type = SQLite

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
