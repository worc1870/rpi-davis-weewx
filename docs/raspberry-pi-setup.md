# Raspberry Pi setup

This document records the software-side setup used on the Raspberry Pi. Keep installation commands here in the order required for rebuilding the system.

## Operating system

Raspberry Pi OS Lite on a Raspberry Pi 4 Model B.


## Connecting RPi 4B to laptop running Ubuntu 24.04 LTS

1. Connect a standard ethernet cable between your Pi 4B and the USB-C adapter on your Ubuntu laptop.
2. Open your Ubuntu Settings app and click on Network (or Wi-Fi, then look for the Wired/USB Ethernet section).
3. Find your USB-C Ethernet adapter connection and click the Gear icon next to it to open its properties.
4. Go to the IPv4 tab.
5. Change the IPv4 Method from Automatic (DHCP) to Shared to other computers.
6. Alternative: If "Shared to other computers" is missing, select Link-Local Only.
7. Click Apply in the top right corner.
8. Turn the USB-C Ethernet connection Off and back On using the toggle switch to force Ubuntu to apply the change. 

```bash
# list USB devices
lsusb
```
Check for something like

```text
Bus 002 Device 006: ID 0bda:8153 Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter
```

```bash
# look for state of device; look for something like enxa0cec815221f; get IP address
ip neighbor
```

```text
10.42.0.225 dev enxa0cec815221f lladdr d8:3a:dd:4b:32:fc STALE
```

```bash
# ssh to RPi 4B
ssh admin@10.42.0.225 
```

Communication now established between laptop and RPi 4B without using WiFi.


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
