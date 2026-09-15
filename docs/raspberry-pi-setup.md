# Raspberry Pi setup

This document records the software-side setup used on the Raspberry Pi. Keep installation commands here in the order required for rebuilding the system.

## Operating system

Raspberry Pi OS Lite on a Raspberry Pi 4 Model B.

## Useful packages

The `sqlite3` command-line client is useful for inspecting the WeeWX database:

```bash
sudo apt update
sudo apt install sqlite3
```

Python 3 is supplied by the OS; the working system used Python 3.13.5.

## Verify WeeWX

```bash
weectl --version
python3 --version
```

Expected versions in the documented installation:

```text
WeeWX 5.5.0
Python 3.13.5
```

## Check the archive database

```bash
sudo sqlite3 /var/lib/weewx/weewx.sdb "PRAGMA table_info(archive);"
```

The documented installation uses:

```text
/var/lib/weewx/weewx.sdb
```

for the SQLite archive database.

## Service startup

WeeWX is run as the supplied systemd service. Enable it so that it starts automatically at boot:

```bash
sudo systemctl enable weewx
```

Check:

```bash
systemctl is-enabled weewx
systemctl status weewx
```
