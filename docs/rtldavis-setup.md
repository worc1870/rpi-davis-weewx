# rtldavis and WeeWX driver setup

This project uses:

- [`lheijst/rtldavis`](https://github.com/lheijst/rtldavis)
- [`lheijst/weewx-rtldavis`](https://github.com/lheijst/weewx-rtldavis)

## rtldavis command

The working configuration uses:

```text
/usr/local/bin/rtldavis -gain 40 -fc 50000 -tf EU -tr 64
```

The equivalent configuration is represented in `weewx.conf` as:

```ini
[Rtldavis]
    cmd = /usr/local/bin/rtldavis -gain 40 -fc 50000
    channel = EU
    iss_channel = 7
    driver = user.rtldavis
```

The driver starts `rtldavis` and receives the decoded observations for WeeWX.

## Verify decoder operation

Check the WeeWX log for lines similar to:

```text
Loading station type Rtldavis (user.rtldavis)
driver version is 0.20
using frequency EU
using iss_channel 7
startup process '/usr/local/bin/rtldavis ...'
```

The exact log text may vary by version.

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
