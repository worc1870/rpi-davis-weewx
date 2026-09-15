# Troubleshooting

## `sqlite3: command not found`

Install the SQLite command-line client:

```bash
sudo apt update
sudo apt install sqlite3
```

## `PermissionError: /var/lib/weewx/csv/weather.csv`

The WeeWX service needs write permission on the CSV directory and file.

Check:

```bash
ls -ld /var/lib/weewx/csv
ls -l /var/lib/weewx/csv/weather.csv
ps -o user,group,cmd -C weewxd
```

On the documented setup the directory is owned by `weewx:weewx`:

```bash
sudo chown -R weewx:weewx /var/lib/weewx/csv
```

## `weeutil.logger` has no attribute `logdbg`

An earlier version of the custom CSV logger used a non-existent `weeutil.logger.logdbg()` call. The current `weewx/csvlogger.py` uses Python's standard `logging` interface instead.

## WeeWX starts and then stops

Inspect:

```bash
sudo journalctl -u weewx -n 50 --no-pager
```

For live logging:

```bash
sudo journalctl -u weewx -f
```

## Check that METRICWX is active

```bash
sudo sqlite3 /var/lib/weewx/weewx.sdb \
"SELECT datetime(dateTime,'unixepoch','localtime'),usUnits,outTemp,windSpeed,rain FROM archive ORDER BY dateTime DESC LIMIT 5;"
```

The documented installation reported `usUnits = 17` and values consistent with METRICWX.

## Check that archive records are one minute apart

```bash
sudo sqlite3 /var/lib/weewx/weewx.sdb \
"SELECT datetime(dateTime,'unixepoch','localtime'),interval FROM archive ORDER BY dateTime DESC LIMIT 10;"
```

## Empty pressure fields

The current Davis ISS data stream does not provide barometric pressure, so `pressure`, `barometer`, and `altimeter` were empty in the tested records. This is a hardware/data-source issue, not a CSV logging problem.
