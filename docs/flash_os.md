# Flash Raspberry Pi OS Lite to an SD card

## Windows
Consult the intenet.

## MacOS
Consult the intenet.

## Linux (Debian)
[Raspberry Pi OS Lite (64-bit)](https://www.raspberrypi.com/software/operating-systems/) is a light-weight operating system. It does not include a desktop environment. It boots up in about 25s or so.

The following instructions are based on using a laptop running Ubuntu 24.04 LTS. 

Install the Raspberry Pi Imager.

```bash
sudo snap install rpi-imager
```
Insert micro SD card into card reader. Plug card reader into USB-C port.

Start the Raspberry Pi Imager via the Ubuntu startup menu.

1. Choose Device: `Raspberry Pi 4`
2. Choose OS: `Raspberry Pi OS (other)` --> `Raspberry Pi OS Lite (64-bit)`
3. Choose Storage: select Micro SD Card drive
4. Click `Next`.
5. On the popup window `Would you like to apply OS customisation settings?` click `EDIT SETTINGS` and settings. I used the following settings.
```text
GENERAL
Hostname: rpi4b
Username: admin
Password: *****
Configure wireless LAN: uncheck (we connect via Ethernet cable)
Time Zone: Europe/London
Keyboard layout: gb

SERVICE
Enable SSH
Use password authentication

OPTIONS
kept unchanged
```
6. Click `Save`.
7. Confirm `Would you like to apply OS customisation settings?` with `YES`.
8. Confirm `Are you sure you want to continue` with `YES`.
9. Wait until the flashing the OS has completed. Click `CONTINUE`, close the Raspberry Pi Imager and remove the SD card from the card reader.

Make sure the RPi 4B is powered off. Insert the SD card into the RPi 4B. 