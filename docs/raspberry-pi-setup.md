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


## Install DS3231 RTC module 

The DS3231 RTC module better than DS1307 because temperature-compensated crystal, significantly more precise (±2 ppm). 

To install and configure a DS3231 RTC module on a Raspberry Pi 4 Model B running Raspberry Pi OS Lite, you must  

- connect the hardware to the GPIO pins
    - Remove power supply from RPi 4B. Insert the DS3231 RTC module into the first 4 inner side pins of the RPi 4B. Connect RPi 4B to laptop and power back up.

- enable the I2C interface
    ```bash
    sudo raspi-config
    ```
    - Navigate Interface Options -> I2C
    - Enable ARM I2C
    - Finish
    ```bash
    sudo nano /boot/firmware/config.txt
    ```
    - Add following lines at the bottom of file.  
    ```text
    dtparam=i2c_arm=on
    dtoverlay=i2c-rtc,ds3231
    ```
    - Close and reboot
    ```bash
    sudo reboot
    ```

- verify hardware connection 
    ```bash
    sudo apt update 
    sudo apt upgrade    # optional
    sudo apt autoclean    # optianal
    sudo apt autoremove    # optional
    sudo apt install i2c-tools 
    sudo i2cdetect -y 1    # Scan the I2C bus to check for the module)
    ```

    Check that <b>68</b> shows <b>UU</b>.

    <b>68</b> means the hardware is detected but waiting for driver initialization.

    <b>UU</b> means the driver successfully locked onto the chip and it is ready for use. 

- Sync time to the RTC Module 
    ```bash
    sudo apt install util-linux-extra
    timedatectl    # check if system time was updated from internet on boot 
    date    # check system time 
    sudo hwclock -w   # Write your accurate system time directly into the DS3231 module 
    sudo hwclock –r   # Read the time directly back from the hardware clock to verify it was written correctly
    ```

- Disable the fake hardware clock (turned out to not be installed) 

    Raspberry Pi OS Lite may contain a backup script called `fake-hwclock`. It creates a mock file checkpoint to guess the time on shutdown, which interferes with your real DS3231 hardware module. it must be purge.
    ```bash
    sudo apt-get -y remove fake-hwclock
    ```

- Verify hardware clock exists 
    ```bash
    ls -l /dev/rtc*
    ```
    ```text
    lrwxrwxrwx 1 root root      4 Jan  1  2000 /dev/rtc -> rtc0 
    crw------- 1 root root 251, 0 Aug 26 21:52 /dev/rtc0
    ```
    The entry /dev/rtc0 is the direct device file for your physical DS3231 module, and /dev/rtc -> rtc0 is a symbolic link created by the system to point the default system clock utilities directly to your hardware module. 

- Disable `systemd-timesyncd` fake-clock fallback (if applicable) 

    Modern Raspberry Pi OS uses `systemd-timesyncd` to manage time syncing. While it relies on internet NTP servers when online, it also saves a timestamp to disk on shutdown to prevent the clock from jumping back to 1970. To let the RTC handle everything flawlessly during boot, you can explicitly ensure the hardware clock takes priority over systemd tracking:
    ```bash
    sudo nano /etc/systemd/timesyncd.conf
    ```
    
    Set `NTP=pool.ntp.org`, this updates the RTC every 11 min if network available.

    Verify everything is working autonomously without network time sync.
    ```bash
    sudo poweroff
    ```

    Unplug the power cable and disconnect your Ethernet cable or Wi-Fi network. Wait a couple of minutes, plug the power back in, and boot it up. Check that date/time is correct.
    ```bash
    date
    ```


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
