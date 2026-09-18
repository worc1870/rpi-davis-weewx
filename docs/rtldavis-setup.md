# rtldavis and WeeWX driver setup

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

WeeWX is software package for logging weather station data and creating graphs. We will use it for logging data only. For the installation I followed steps from [here](https://www.weewx.com/docs/5.5/quickstarts/debian/).

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

    Useful commands for checking that WeeWX is working.
    ```bash
    sudo systemctl status weewx   # check status
    sudo systemctl start weewx    # stop weewx
    sudo systemctl restart weewx    # restart weewx
    sudo systemctl stop weewx    # stop weewx
    sudo journalctl -u weewx   # check system log for weewx
    ```

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


## Install rtldavis

The rtldavis project is the implementation of a receiver for Davis wireless weather stations that makes use of RTL-SDR dongles. It was originally coded up by GitHub user [bemasher](https://github.com/bemasher/rtldavis) in 2015. We here use a modified fork of the original from GitHub user [lheijst](https://github.com/lheijst/rtldavis) from around 2019. It is the preferred fork for Davis stations sold in European that transmit at 868.0–868.6 MHz. It incorporates explicit tuning adjustments (-tf and -tr frequency options) required to lock onto shifting EU signals.

The rtldavis installation is in parts based on the instructions from [here](https://www.instructables.com/Davis-Van-ISS-Weather-Station-With-Raspbe/).

- Install packes needed
    ```bash
        sudo apt-get install golang git cmake
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
    git clone https://github.com/lheijst/rtldavis
    cd rtldavis
    go mod init github.com/lheijst/rtldavis  # creates temporary go.mod
    go get -d ./...    # some dependencies incompatible! --> remove vendor
    rm -rf vendor
    go mod tidy
    go install -v .     # should not show any errors
    ~/go/bin/rtldavis -v     # check if the binary works
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
    Add the following lines at the end of the file.
    ```text
    [Rtldavis]
        # Change this path to match exactly where your compiled rtldavis binary resides
        # pass -tf EU and -tr 64 outside the command as channel and iss_channel
        cmd = /usr/local/bin/rtldavis -gain 40 -fc 50000

        # Let the driver handle the region and your Channel 7 configuration natively
        channel = EU
        iss_channel = 7

        driver = user.rtldavis

    ```
You may have to move the binary file to `/usr/local/bin/rtldavis`.


## Testing frequency hopping and frequency offset

In the European versions of Davis Vantage weather stations, the ISS does not transmit continuously on one fixed radio frequency. Instead, it repeatedly changes (or hops) between a small set of frequencies in the 868 MHz band. The ISS uses Frequency-Hopping Spread Spectrum (FHSS) technology. Because the ISS hopes every 2.5 seconds to the next frequency is why the RTL-SDR receiver cannot simply be tuned to one frequency and left there.

Davis weather station EU/UK models operate in the 868.0–868.6 MHz frequency band. Hard-coded EU channels in `/home/admin/rtldavis/protocol/protocol.go` are 
```text
868077250, 868197250, 868317250, 868437250, 868557250, // EU test 20190324 
```

Execute a test scan to check if packets are received from the ISS (takes about 20 min).
- Do NOT us `-tf EU` together with the frequency range settings
- Use binary codes for setting transmission channel
- Set gain to 40 manually if needed
- a step frequency of `50000` may also be used
```bash
/usr/local/bin/rtldavis -tr 64 -startfreq 868000000 -endfreq 868700000 -stepfreq 25000
```
Output may look like the following.
```text
10:05:59.559892 rtldavis.go VERSION=0.15
10:05:59.560125 tr=64 fc=0 ppm=0 gain=0 maxmissed=51 ex=0 receiveWindow=300 actChan=[6] maxChan=1
10:05:59.560163 undefined=false verbose=false disableAfc=false deviceString=0
10:05:59.560172 TEST: startFreq=868000000 endFreq=868700000 stepFreq=25000
10:05:59.562214 BitRate: 19200
10:05:59.562238 SymbolLength: 14
10:05:59.562246 SampleRate: 268800
10:05:59.562254 Preamble: 1100101110001001
10:05:59.562259 PreambleSymbols: 16
10:05:59.562265 PreambleLength: 224
10:05:59.562270 PacketSymbols: 80
10:05:59.562276 PacketLength: 1120
10:05:59.562282 BlockSize: 512
10:05:59.562288 BufferLength: 2048
Found Rafael Micro R820T tuner
10:05:59.936856 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:0 Transmitter:0}
Exact sample rate is: 268800.001367 Hz
10:06:00.061911 GetTunerGain: 0 Db
10:06:00.061964 SetFreqCorrection 0 ppm Successful
10:06:00.065518 Init channels: wait max 20 seconds for a message of each transmitter
10:06:41.192163 TESTFREQ 1: Frequency 868000000: NOK
10:07:01.755910 TESTFREQ 2: Frequency 868025000: NOK
10:07:22.319770 TESTFREQ 3: Frequency 868050000: NOK
10:07:42.883332 TESTFREQ 4: Frequency 868075000: NOK
10:08:03.447277 TESTFREQ 5: Frequency 868100000: NOK
10:08:15.727513 TESTFREQ 6: Frequency 868125000 (freqCorr=0): OK, msg.data: A602D9CE2900F2B6
10:08:36.290624 TESTFREQ 7: Frequency 868150000: NOK
10:08:56.854212 TESTFREQ 8: Frequency 868175000: NOK
10:09:17.417901 TESTFREQ 9: Frequency 868200000: NOK
10:09:37.981643 TESTFREQ 10: Frequency 868225000: NOK
10:09:52.663495 TESTFREQ 11: Frequency 868250000 (freqCorr=0): OK, msg.data: 8602DD254B0030C7
10:10:13.227267 TESTFREQ 12: Frequency 868275000: NOK
10:10:33.790755 TESTFREQ 13: Frequency 868300000: NOK
10:10:54.354616 TESTFREQ 14: Frequency 868325000: NOK
10:11:14.918481 TESTFREQ 15: Frequency 868350000: NOK
10:11:35.482357 TESTFREQ 16: Frequency 868375000: NOK
10:11:56.045890 TESTFREQ 17: Frequency 868400000: NOK
10:12:16.609781 TESTFREQ 18: Frequency 868425000: NOK
10:12:37.173668 TESTFREQ 19: Frequency 868450000: NOK
10:12:57.737557 TESTFREQ 20: Frequency 868475000: NOK
10:13:18.301094 TESTFREQ 21: Frequency 868500000: NOK
10:13:38.864982 TESTFREQ 22: Frequency 868525000: NOK
10:13:59.428870 TESTFREQ 23: Frequency 868550000: NOK
10:14:19.992760 TESTFREQ 24: Frequency 868575000: NOK
10:14:28.788938 TESTFREQ 25: Frequency 868600000 (freqCorr=0): OK, msg.data: 5604FAFF7100779E
10:14:49.352717 TESTFREQ 26: Frequency 868625000: NOK
10:15:09.916610 TESTFREQ 27: Frequency 868650000: NOK
10:15:30.480153 TESTFREQ 28: Frequency 868675000: NOK
10:15:51.044062 TESTFREQ 29: Frequency 868700000: NOK
10:15:51.044156 Test reached endfreq; test ended
```
Lines like `10:08:15.727513 TESTFREQ 6: Frequency 868125000 (freqCorr=0): OK, msg.data: A602D9CE2900F2B6` mean a coded packet from the ISS is received.

Identify the frequency offset. In my case it was roughly 50000 Hz. It is possible that this is always the case for European stations as it is the same value as found by [guidocioni](https://www.instructables.com/Davis-Van-ISS-Weather-Station-With-Raspbe/).

Now try use the offset frequency to test if the frequency hopping sequence is recognised and packets can be received every 2.5 seconds.
```bash
/usr/local/bin/rtldavis -tf EU -tr 64 -gain 40 -fc 50000
```
Output may look like the following.
```text
11:17:44.380561 rtldavis.go VERSION=0.15
11:17:44.381086 tr=64 fc=50000 ppm=0 gain=40 maxmissed=51 ex=0 receiveWindow=300 actChan=[6] maxChan=1
11:17:44.381226 undefined=false verbose=false disableAfc=false deviceString=0
11:17:44.381973 BitRate: 19200
11:17:44.382012 SymbolLength: 14
11:17:44.382033 SampleRate: 268800
11:17:44.382058 Preamble: 1100101110001001
11:17:44.382078 PreambleSymbols: 16
11:17:44.382095 PreambleLength: 224
11:17:44.382111 PacketSymbols: 80
11:17:44.382128 PacketLength: 1120
11:17:44.382145 BlockSize: 512
11:17:44.382162 BufferLength: 2048
Found Rafael Micro R820T tuner
11:17:44.783196 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:0 Transmitter:0}
Exact sample rate is: 268800.001367 Hz
11:17:44.919263 Supported tuner gain: 0 Db 9 Db 14 Db 27 Db 37 Db 77 Db 87 Db 125 Db 144 Db 157 Db 166 Db 197 Db 207 Db 229 Db 254 Db 280 Db 297 Db 328 Db 338 Db 364 Db 372 Db 386 Db 402 Db 421 Db 434 Db 439 Db 445 Db 480 Db 496 Db
11:17:44.937479 SetTunerGain 40 Successful
11:17:44.937540 GetTunerGain: 40 Db
11:17:44.937553 SetFreqCorrection 0 ppm Successful
11:17:44.940853 Init channels: wait max 20 seconds for a message of each transmitter
11:17:46.982529 TRANSMITTER 6 SEEN
11:17:46.982585 Hop: {ChannelIdx:2 ChannelFreq:868317250 FreqError:0 Transmitter:6}
11:17:49.921871 8601CD25BB00D673 2 0 0 0 0 msg.ID=6
11:17:49.921951 Hop: {ChannelIdx:4 ChannelFreq:868557250 FreqError:0 Transmitter:6}
11:17:52.859061 E602C93F0100D82C 3 0 0 0 0 msg.ID=6
11:17:52.859168 Hop: {ChannelIdx:1 ChannelFreq:868197250 FreqError:0 Transmitter:6}
11:17:55.796278 5602D0FF7100E5FE 4 0 0 0 0 msg.ID=6
11:17:55.796367 Hop: {ChannelIdx:3 ChannelFreq:868437250 FreqError:0 Transmitter:6}
11:17:58.733300 6602E53103000913 5 0 0 0 0 msg.ID=6
11:17:58.733377 Hop: {ChannelIdx:0 ChannelFreq:868077250 FreqError:-79 Transmitter:6}
11:18:02.034087 ID:6 packet missed (1), missed per freq: [1 0 0 0 0]
11:18:02.034248 Hop: {ChannelIdx:2 ChannelFreq:868317250 FreqError:164 Transmitter:6}
11:18:04.607566 E602DD3F0100097A 6 0 0 0 0 msg.ID=6
11:18:04.607644 Hop: {ChannelIdx:4 ChannelFreq:868557250 FreqError:122 Transmitter:6}
```
This now confirms that the RTL-SDR dongle receives the coded packets from the ISS. Next step is to pass those packets on to WeeWX for decoding and saving into a database.






























## rtldavis command

The working configuration as contained in `weewx.conf`:

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
