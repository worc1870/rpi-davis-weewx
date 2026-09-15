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


## Install useful packages

The `sqlite3` command-line client is useful for inspecting the WeeWX database:

```bash
sudo apt update
sudo apt install sqlite3
```

Python 3 is supplied by the OS; the working system used Python 3.13.5.


## Install and configure DS3231 RTC module 

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

## Setup the RTL-SDR Blog Dongle V3 

Because Davis stations use Frequency Hopping Spread Spectrum (FHSS) technology over the 868 MHz band in Europe, standard generic SDR software like rtl_433 struggles to track the hopping packets consistently. Instead, use `rtldavis`, a specialized tool explicitly written to handle the Davis FHSS sequence. 

The setup involves
- blacklisting the default TV tuner drivers
- installing the RTL-SDR core libraries
- compiling rtldavis
- piping that data into software like WeeWX to log and write to CSV.

<b>Use a USB 2.0 port (Black)</b>: Plug the dongle into one of the black USB 2.0 ports on your Raspberry Pi. The blue USB 3.0 ports on the Raspberry Pi 4 and Pi 5 generate a massive amount of high-frequency electronic noise. This noise bleeds heavily into the 800–900 MHz radio spectrum and can completely deafen your SDR receiver. 

<b>Consider a USB Extension Cable</b>: If your Pi is inside a metal case or near a Wi-Fi router, use a short (15–50 cm) shielded USB extension cable to physically separate the dongle from the Pi's mainboard. This drops the noise floor dramatically. 

- Install Core System Dependencies, the tools required to compile the SDR software.

    ```bash
    sudo apt update 
    sudo apt install -y git cmake build-essential libusb-1.0-0-dev golang pkg-config
    ```
- Block Default TV Tuner Drivers

    ```bash
    sudo nano /etc/modprobe.d/blacklist-rtl.conf
    ```
    Add following lines and save.
    ```text
    blacklist dvb_usb_rtl28xxu
    blacklist rtl2832
    blacklist rtl2830
    ```
- Install the RTL-SDR Blog Driver Library

    Compile the official drivers that allow applications to communicate with the dongle. Do <b>NOT</b> install `librtlsdr-dev` via the package manager.

    ```bash
    sudo apt update
    sudo apt install libusb-1.0-0-dev git cmake pkg-config
    git clone https://github.com/rtlsdrblog/rtl-sdr-blog
    cd rtl-sdr-blog/
    mkdir build
    cd build
    cmake ../ -DINSTALL_UDEV_RULES=ON
    make
    sudo make install
    sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
    sudo ldconfig
    sudo reboot
    ```
    
- Blacklist Conflicting DVB-T Kernel Modules 

    ```bash
    echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
    ```
    ```bash
    cat <<EOF | sudo tee /etc/modprobe.d/blacklist-rtl.conf
    blacklist dvb_usb_rtl28xxu
    blacklist rtl2832
    blacklist rtl2830
    EOF
    ```
    ```bash
    sudo reboot
    ```

    After reboot, confirm the module isn’t loaded.
    ```bash
    lsmod | grep -E 'dvb|rtl2832'    # should return nothing
    ```

- Verify the dongle is detected

    Turn off RPi 4B, insert dongle into black USB v2 port, boot up. 

    ```bash
    lsusb
    ```
    Output:
    ```text
    Bus 001 Device 005: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
    ```

    Lists supported tuners. Ignore “No E4000 tuner found, aborting.” 
    ```bash
    rtl_test –t
    ``` 

    If `rtl_test` fails with “permission denied”, check that user is in the `plugdev` (or similar) group and that the udev rule sets MODE="0660" and GROUP="plugdev" (or your chosen group).

- Confirm you can use the dongle without root.
    ``` bash
    rtl_fm -f 915M -N -n 100000 > /dev/null
    ```
    
    If that runs without “permission denied”, the udev rules are fine.


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
