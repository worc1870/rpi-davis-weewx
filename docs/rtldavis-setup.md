# rtldavis and WeeWX Setup

This project uses:

- [`lheijst/rtldavis`](https://github.com/lheijst/rtldavis)
- [`lheijst/weewx-rtldavis`](https://github.com/lheijst/weewx-rtldavis)

## Setup the RTL-SDR Blog Dongle V3 

Because Davis stations use Frequency Hopping Spread Spectrum (FHSS) technology over the 868 MHz band in Europe, standard generic SDR software like rtl_433 struggles to track the hopping packets consistently. Instead, use `rtldavis`, a specialized tool explicitly written to handle the Davis FHSS sequence. 

The setup involves
- blacklisting the default TV tuner drivers
- installing the RTL-SDR core libraries
- compiling rtldavis
- piping that data into software like WeeWX

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

    Unplug the RTL-SDR dongle.

    Compile the official drivers that allow applications to communicate with the dongle. Do <b>NOT</b> install `librtlsdr-dev` via the package manager.

    ```bash
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
    sudo poweroff
    ```

- Plug the RTL-SDR dongle back into the RPi_4B (black USB port) and boot up RPi-4B.

    After reboot, confirm the module isn’t loaded.
    ```bash
    lsmod | grep -E 'dvb|rtl2832'    # should return nothing
    ```

- Verify the dongle is detected

    Turn off RPi 4B, insert dongle into black USB v2 port, boot up. 

    ```bash
    lsusb
    ```
    Output should be something like:
    ```text
    Bus 001 Device 005: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
    ```

    Lists supported tuners. Ignore “No E4000 tuner found, aborting.” 
    ```bash
    rtl_test –t
    ``` 
    Output should look something like:
    ```text
    Found 1 device(s):
      0:  Realtek, RTL2838UHIDIR, SN: 00000001

    Using device 0: Generic RTL2832U OEM
    Found Rafael Micro R820T tuner
    ```

    If `rtl_test` fails with “permission denied”, check that user is in the `plugdev` (or similar) group and that the udev rule sets MODE="0660" and GROUP="plugdev" (or your chosen group).


## Install WeeWX

WeeWX is software package for logging weather station data and creating graphs. It is used here for data logging only. The following installation precedure is based on this [page](https://www.weewx.com/docs/5.5/quickstarts/debian/).

- Tell your system to trust weewx.com.
    ```bash
    sudo apt update
    sudo apt install -y wget gnupg
    wget -qO - https://weewx.com/keys.html | sudo gpg --dearmor --output /etc/apt/trusted.gpg.d/weewx.gpg
    ```
- Tell apt where to find the WeeWX repository.
    ```bash
    echo "deb [arch=all] https://weewx.com/apt/python3 buster main" | sudo tee /etc/apt/sources.list.d/weewx.list
    ```
- Install WeeWX
    ```bash
    sudo apt update
    sudo apt install weewx
    ```

    During the setup I used the following settings:
    - Location: Oxford Test
    - Lat/Lon: 51.75889, -1.25375
    - Altitude: 63 m
    - Unit system: metricwx
    - Weather station type: Simulation 
    - do not register the station with WeatherUnderground, can be done later if needed

- Verify WeeWX

    ```bash
    weectl --version
    python3 --version
    ```

    Expected versions in the documented installation:

    ```text
    WeeWX 5.5.0
    Python 3.13.5
    ```

- Useful commands for checking that WeeWX is working later. At this stage no data are being received yet.
    ```bash
    sudo systemctl status weewx   # check status
    sudo systemctl start weewx    # stop weewx
    sudo systemctl restart weewx    # restart weewx
    sudo systemctl stop weewx    # stop weewx
    sudo journalctl -u weewx   # check system log for weewx
    ```


## Install rtldavis

The `rtldavis` project is the implementation of a receiver for Davis wireless weather stations that makes use of RTL-SDR dongles. It was originally coded up by GitHub user [bemasher](https://github.com/bemasher/rtldavis) in 2015. We here use a modified fork of the original from GitHub user [lheijst](https://github.com/lheijst/rtldavis) from around 2019. It is the preferred fork for Davis stations sold in European that transmit at 868.0–868.6 MHz. It incorporates explicit tuning adjustments (-tf and -tr frequency options) required to lock onto shifting EU signals.

The rtldavis installation is in parts based on the instructions from [here](https://www.instructables.com/Davis-Van-ISS-Weather-Station-With-Raspbe/).

- Make sure the following packes are installed
    ```bash
        sudo apt install golang git cmake
    ```

- Install `librtlsdr` from source
    ```bash
    git clone https://github.com/steve-m/librtlsdr.git
    cd librtlsdr
    mkdir build
    cd build
    cmake ../ -DINSTALL_UDEV_RULES=ON
    make
    sudo make install
    sudo ldconfig
    ```

- Add some path to your profile
    ```bash
    sudo nano ~/.profile  
    ```
    Add the following lines at the end of the file
    ```text
    export GOROOT=/usr/lib/go
    export GOPATH=$HOME
    export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
    ```
    Source profile
    ```bash
    source ~/.profile
    ```
- Get the `rtldavis` package
    ```bash
    cd    # go back to root of user area
    git clone https://github.com/lheijst/rtldavis
    cd rtldavis
    go mod init github.com/lheijst/rtldavis  # creates temporary go.mod
    go get -d ./...    # some dependencies incompatible! --> remove vendor
    rm -rf vendor
    go mod tidy
    go install -v .     # should not show any errors
    ```
    Check that the rtldavis binary works. The following command will start the tuner with "emit verbose debug messages" enabled.
    ```bash
    ~/bin/rtldavis -v
    ```


## Configure rtldavis to work with WeeWX

- Install `weewx-rtldavis` driver extension
    ```bash
    sudo systemctl stop weewx   # make sure WeeWX stopped
    sudo weectl extension install https://github.com/lheijst/weewx-rtldavis/archive/master.zip
    ```
- Configure WeeWX
    ```bash
    sudo nano /etc/weewx/weewx.conf
    ```
    Add the following lines at the end of the file. Edit the ISS channel according to your Davis weather station setting.
    ```text
    [Rtldavis]
        # Change this path to match exactly where your compiled rtldavis binary resides
        # pass -tf EU and -tr 64 outside the command as channel and iss_channel
        cmd = /usr/local/bin/rtldavis -gain 40 -fc 50000

        # Let the driver handle the region and your Channel 1 configuration natively
        channel = EU
        iss_channel = 1

        driver = user.rtldavis

    ```

- Move the binary file to `/usr/local/bin/rtldavis`.
    ```bash
    sudo mv /home/admin/bin/rtldavis /usr/local/bin/rtldavis
    sudo chown root:root /usr/local/bin/rtldavis
    sudo chmod 755 /usr/local/bin/rtldavis
    ```


## Testing frequency hopping and frequency offset

In the European versions of Davis Vantage weather stations, the ISS does not transmit continuously on one fixed radio frequency. Instead, it repeatedly changes (or hops) between a small set of frequencies in the 868 MHz band. The ISS uses Frequency-Hopping Spread Spectrum (FHSS) technology. Because the ISS hopes every 2.5 seconds to the next frequency is why the RTL-SDR receiver cannot simply be tuned to one frequency and left there.

Davis weather station EU/UK models operate in the 868.0–868.6 MHz frequency band. Hard-coded EU channels in `/home/admin/rtldavis/protocol/protocol.go` are 
```text
868077250, 868197250, 868317250, 868437250, 868557250, // EU test 20190324 
```

Execute a test scan to check if packets are received from the ISS (takes about 20 min).
- Use binary codes for setting transmission channel
- Set gain to 40 explicitly (default seems to be 0)
- a step frequency of `50000` may also be used

From `https://github.com/lheijst/rtldavis` documentation
```text
-tr [transmitters]
    	code of the stations to listen for: 
        tr1=1 tr2=2 tr3=4 tr4=8 tr5=16 tr6=32 tr7=64 tr8=128
        or the Davis syntax (first transmitter ID has value 0):
        ID 0=1 ID 1=2 ID 2=4 ID 3=8 ID 4=16 ID 5=32 ID 6=64 ID 7=128
        When two or more transmitters are combined, add the numbers.
        Example: ID0 and ID2 combined is 1 + 4 => -tr 5
        
        Default = -tr 1 (ID 0)

  -tf [tranceiver frequencies]
        EU or US
        Default = -tf EU
```

Run
```bash
/usr/local/bin/rtldavis -tf EU -tr 1 -gain 40 -startfreq 868000000 -endfreq 868700000 -stepfreq 25000
```

Wait until the test has completed. This will take 10 minutes or so.

Output may look like the following.
```text
16:34:42.500044 rtldavis.go VERSION=0.15
16:34:42.500620 tr=1 fc=0 ppm=0 gain=40 maxmissed=51 ex=0 receiveWindow=300 actChan=[0] maxChan=1
16:34:42.500709 undefined=false verbose=false disableAfc=false deviceString=0
16:34:42.500734 TEST: startFreq=868000000 endFreq=868700000 stepFreq=25000
16:34:42.501494 BitRate: 19200
16:34:42.501535 SymbolLength: 14
16:34:42.501555 SampleRate: 268800
16:34:42.501573 Preamble: 1100101110001001
16:34:42.501589 PreambleSymbols: 16
16:34:42.501606 PreambleLength: 224
16:34:42.501621 PacketSymbols: 80
16:34:42.501636 PacketLength: 1120
16:34:42.501653 BlockSize: 512
16:34:42.501668 BufferLength: 2048
Found Rafael Micro R820T tuner
16:34:42.908886 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:0 Transmitter:0}
Exact sample rate is: 268800.001367 Hz
16:34:43.046411 Supported tuner gain: 0 Db 9 Db 14 Db 27 Db 37 Db 77 Db 87 Db 125 Db 144 Db 157 Db 166 Db 197 Db 207 Db 229 Db 254 Db 280 Db 297 Db 328 Db 338 Db 364 Db 372 Db 386 Db 402 Db 421 Db 434 Db 439 Db 445 Db 480 Db 496 Db 
16:34:43.064863 SetTunerGain 40 Successful
16:34:43.064899 GetTunerGain: 40 Db
16:34:43.064911 SetFreqCorrection 0 ppm Successful
16:34:43.068303 Init channels: wait max 17 seconds for a message of each transmitter
16:35:18.946621 TESTFREQ 1: Frequency 868000000: NOK
16:35:36.885653 TESTFREQ 2: Frequency 868025000: NOK
16:35:54.824690 TESTFREQ 3: Frequency 868050000: NOK
16:36:12.763718 TESTFREQ 4: Frequency 868075000: NOK
16:36:30.702746 TESTFREQ 5: Frequency 868100000: NOK
16:36:39.938891 TESTFREQ 6: Frequency 868125000 (freqCorr=0): OK, msg.data: 8000002DCD0070BF
16:36:57.878122 TESTFREQ 7: Frequency 868150000: NOK
16:37:15.817151 TESTFREQ 8: Frequency 868175000: NOK
16:37:33.756190 TESTFREQ 9: Frequency 868200000: NOK
16:37:51.695201 TESTFREQ 10: Frequency 868225000: NOK
16:38:04.498937 TESTFREQ 11: Frequency 868250000 (freqCorr=757): OK, msg.data: 4000000085008E7D
16:38:22.437889 TESTFREQ 12: Frequency 868275000: NOK
16:38:40.376918 TESTFREQ 13: Frequency 868300000: NOK
16:38:58.315949 TESTFREQ 14: Frequency 868325000: NOK
16:39:16.254968 TESTFREQ 15: Frequency 868350000: NOK
16:39:34.194353 TESTFREQ 16: Frequency 868375000: NOK
16:39:52.133382 TESTFREQ 17: Frequency 868400000: NOK
16:40:10.072399 TESTFREQ 18: Frequency 868425000: NOK
16:40:28.011430 TESTFREQ 19: Frequency 868450000: NOK
16:40:45.950464 TESTFREQ 20: Frequency 868475000: NOK
16:41:03.889492 TESTFREQ 21: Frequency 868500000: NOK
16:41:21.828541 TESTFREQ 22: Frequency 868525000: NOK
16:41:39.767537 TESTFREQ 23: Frequency 868550000: NOK
16:41:57.706568 TESTFREQ 24: Frequency 868575000: NOK
16:42:05.365793 TESTFREQ 25: Frequency 868600000 (freqCorr=924): OK, msg.data: 500000FF7500485B
16:42:23.304779 TESTFREQ 26: Frequency 868625000: NOK
16:42:41.243801 TESTFREQ 27: Frequency 868650000: NOK
16:42:59.182826 TESTFREQ 28: Frequency 868675000: NOK
16:43:17.121878 TESTFREQ 29: Frequency 868700000: NOK
16:43:17.122056 Test reached endfreq; test ended
```

Lines like `16:42:05.365793 TESTFREQ 25: Frequency 868600000 (freqCorr=924): OK, msg.data: 500000FF7500485B` mean a coded packet from the ISS is received.

Identify the frequency offset (`-fc` value). In my case it was roughly 50000 Hz. It is possible that this is always the case for European stations as it is the same value as found by [guidocioni](https://www.instructables.com/Davis-Van-ISS-Weather-Station-With-Raspbe/).

Now try use the offset frequency to test if the frequency hopping sequence is recognised and packets can be received every 2.5 seconds.
```bash
/usr/local/bin/rtldavis -tf EU -tr 1 -gain 40 -fc 50000
```
Output may look like the following.
```text
16:45:24.826059 rtldavis.go VERSION=0.15
16:45:24.826615 tr=1 fc=50000 ppm=0 gain=40 maxmissed=51 ex=0 receiveWindow=300 actChan=[0] maxChan=1
16:45:24.826700 undefined=false verbose=false disableAfc=false deviceString=0
16:45:24.827572 BitRate: 19200
16:45:24.827617 SymbolLength: 14
16:45:24.827635 SampleRate: 268800
16:45:24.827653 Preamble: 1100101110001001
16:45:24.827670 PreambleSymbols: 16
16:45:24.827686 PreambleLength: 224
16:45:24.827701 PacketSymbols: 80
16:45:24.827718 PacketLength: 1120
16:45:24.827735 BlockSize: 512
16:45:24.827752 BufferLength: 2048
Found Rafael Micro R820T tuner
16:45:25.232238 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:0 Transmitter:0}
Exact sample rate is: 268800.001367 Hz
16:45:25.368299 Supported tuner gain: 0 Db 9 Db 14 Db 27 Db 37 Db 77 Db 87 Db 125 Db 144 Db 157 Db 166 Db 197 Db 207 Db 229 Db 254 Db 280 Db 297 Db 328 Db 338 Db 364 Db 372 Db 386 Db 402 Db 421 Db 434 Db 439 Db 445 Db 480 Db 496 Db 
16:45:25.386523 SetTunerGain 40 Successful
16:45:25.386557 GetTunerGain: 40 Db
16:45:25.386568 SetFreqCorrection 0 ppm Successful
16:45:25.389925 Init channels: wait max 17 seconds for a message of each transmitter
16:45:38.047266 TRANSMITTER 0 SEEN
16:45:38.047391 Hop: {ChannelIdx:2 ChannelFreq:868317250 FreqError:0 Transmitter:0}
16:45:40.609121 500000FF7500485B 2 0 0 0 0 msg.ID=0
16:45:40.609201 Hop: {ChannelIdx:4 ChannelFreq:868557250 FreqError:0 Transmitter:0}
16:45:43.171095 8000002DFD00752A 3 0 0 0 0 msg.ID=0
16:45:43.171180 Hop: {ChannelIdx:1 ChannelFreq:868197250 FreqError:0 Transmitter:0}
16:45:45.734784 4000000085008E7D 4 0 0 0 0 msg.ID=0
16:45:45.734888 Hop: {ChannelIdx:3 ChannelFreq:868437250 FreqError:0 Transmitter:0}
16:45:48.296642 E000008005004F97 5 0 0 0 0 msg.ID=0
16:45:48.296720 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:93 Transmitter:0}
16:45:50.858543 500000FF7500485B 6 0 0 0 0 msg.ID=0
16:45:50.858619 Hop: {ChannelIdx:2 ChannelFreq:868317250 FreqError:399 Transmitter:0}
16:45:53.420458 8000002DFD00752A 7 0 0 0 0 msg.ID=0
16:45:53.420553 Hop: {ChannelIdx:4 ChannelFreq:868557250 FreqError:238 Transmitter:0}
16:45:55.984126 9000000005003151 8 0 0 0 0 msg.ID=0
16:45:55.984201 Hop: {ChannelIdx:1 ChannelFreq:868197250 FreqError:459 Transmitter:0}
```
Look for lines like `16:45:55.984126 9000000005003151 8 0 0 0 0 msg.ID=0`. They mean that a packet is received from the ISS.

This now confirms that the RTL-SDR dongle receives the coded packets from the ISS. Next step is to pass those packets on to WeeWX for decoding and saving into a database.






























