# Flash Raspberry Pi OS Lite to an SD card

## Windows
Download the latest version of the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and flash `Raspberry Pi OS Lite` to an SD card.


## MacOS
Download the latest version of the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and flash `Raspberry Pi OS Lite` to an SD card.


## Linux (Debian)
[Raspberry Pi OS Lite (64-bit)](https://www.raspberrypi.com/software/operating-systems/) is a light-weight operating system. It does not include a desktop environment. It boots up in about 25s or so.

The following instructions are based on using a laptop running Ubuntu 24.04 LTS. 

Insert micro SD card into card reader. Plug card reader into USB-C port.

Install the Raspberry Pi Imager. It was important to get the Raspberry Pi Imager version 2.*, because version 1.9 did not created the user correctly and also did not enable SSH. It had something to do with the Raspberry Pi OS Lite (Trixie) image to be flashed using the newer `cloudinit-rpi` customisation mechanism.

Do NOT use the following command, as it installed the old version.
```bash
sudo snap install rpi-imager
```

Instead, download the latest AppImage of the Raspberry Pi Imager directly from the Raspberry Pi [website](https://www.raspberrypi.com/software/).

Change permissions and run it from the command line.
```bash
chmod +x imager_2.0.11.1_amd64.AppImage
```

Start the Raspberry Pi Imager from the command line. You may get asked to for root credentials.
```bash
./imager_2.0.11.1_amd64.AppImage
```

1. Device: `Raspberry Pi 4`
2. OS: `Raspberry Pi OS (other)` --> `Raspberry Pi OS Lite (64-bit)`
3. Storage Device: select Micro SD Card drive
4. Customaisation
    ```text
    Hostname: rpi
    Localisation:
        Capital city: London
        Time zone: Europe/London
        Keyboard layout: gb
    Username:
        Username: admin
        Password: ****
        Confirm passowrd: ****
    Wi-Fi: leave everything blank as we use ethernet cable to SSH
    SSH authentication: enable
        Use password authentication
    Raspberry Pi Connect: disable
    ```
5. Click `WRITE` button and confirm that all data will be erased from SD card. Wait until writing is complete and click `FINISH`. The Raspberry Pi Imager will close automatically.

Optional, check that the user `admin` was created and SSH was enabled directly on the SD card. Remove SD card from card reader and reinsert it. The check output from following commands.
```bash
sudo cat /media/worc1870/bootfs/user-data
```

Make sure the RPi 4B is powered off. Insert the SD card into the RPi 4B. 