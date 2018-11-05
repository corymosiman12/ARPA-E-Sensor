# Intro
This page is meant to describe the process for getting the UV4L library up and running on a Raspberry Pi.  UV4L allows the pi to act as a streaming video server, which can be connected to using `OpenCV` on a client side application.

1. The pi must be running the `stretch` OS (didn't work when I tried on `jessie`).  Type `$ cat /etc/os-release` to check OS version.  If not, follow the guide [here](https://www.raspberrypi.org/documentation/installation/noobs.md).
2. The camera must be enabled on the pi.  Run `$ sudo raspi-config`, then go to `Interfacing Options` and enable.
3. We also want to enable `ssh`, so do that in the same `Interfacing Options` as well.
4. Enable SPI, I2C, SSH, Camera
3. For the most part, this wiki will follow the install [here](https://www.linux-projects.org/uv4l/installation/).  I have condensed it to only the commands we need below.  This will require an internet connection on the pi.


## If need to reset time/date:
`$ sudo date --set='TZ="America/Denver" 8 Oct 2017 14:32' ` (with current time and date)
Or if you run `$ date` at cmd line, it says old date.  Run `$ timedatectl`, run `$ date` again - should be updated
Rename pi name (need to change in two files on pi)
`$ sudo nano /etc/hostname`, and change name to 'BS1' or similar then rebooting.
then just go to: `$ sudo nano /etc/hosts` 
and make sure the line with `127.0.1.1` looks like:
```127.0.1.1          <our_hostname>```
where `<our_hostname>` would be BS3 or whatever.


# First
To free up some space and limit the number of packages we will eventually install, we are going to remove our wolfram and libreoffice packages:
1. `$ sudo apt-get purge wolfram-engine`
2. `$ sudo apt-get clean && sudo apt-get autoremove`
3. `$ sudo apt-get remove --purge libreoffice*`
4. `$ sudo apt-get clean && sudo apt-get autoremove`
5. `$ sudo reboot`
6. `$ sudo apt update && sudo apt upgrade`

# UV4L on the Pi
Open a terminal and type:
1. `$ curl http://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -` <br />

Add the following line to the end of the file `/etc/apt/sources.list` by typing: <br />

2. `$ sudo nano /etc/apt/sources.list` at the command line <br />

3. Then add at the end of the file: `deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main`

Next, update, fetch, and install uv4l packages: <br />
4. `$ sudo apt-get update` <br />
5. `$ sudo apt-get install uv4l uv4l-raspicam` <br />

We want the driver to load at boot, so type the following <br />
6. `$ sudo apt-get install uv4l-raspicam-extras` <br />

Install the front-end server: <br />
7. `$ sudo apt-get install uv4l-server uv4l-uvc uv4l-xscreen uv4l-mjpegstream uv4l-dummy uv4l-raspidisp` <br />

8. Reboot the pi. <br />

By default, the streaming video server will run on port 8080.  You should now be able to access the video server from a web-browser by typing in `localhost:8080`.  Clicking on the MJPEG/Stills stream will show you the stream.  The `Control Panel` tab will allow you to adjust settings.  I found that reducing the resolution to 3x our target (112x112 is target of WISPCam), so 336x336, gives us minimal lag time.

## Raspicam Options
Edit the raspicam default options to use a lower resolution and framerate and use mjpeg streaming.  Set the resolution to 336x336 and the framerate to 2fps.  This is done via:
`$ sudo nano /etc/uv4l/uv4l-raspicam.conf`

Find the section labeled `raspicam driver options`.  In this section, modify :
```
encoding = mjpeg
width = 336
height = 336
framerate = 2
```

Restart the UV4L server, and you should see these defaults change.  This command can be run at anytime to restart the UV4L server.
`$ sudo service uv4l_raspicam restart`

## Streaming Over the Network
Now, to test the pi running over the network:
1. Connect the pi to on our network.
2. Check the IP address of the pi using `$ ifconfig`.
3. Connect your computer to the same network, and access at the browser through: `[piIpAddress]:8080`, i.e. `192.168.1.104:8080`.  You should now have the same stuff available as if you were accessing it through the localhost.

# Environment Setup
This is a combination of the update posted in [this install guide](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961), addressing the [errors noted here](https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo).  Note that parts 1 and 2 are just to get the virtualenv setup.  Once we are in the virtualenv, it follows the first install guide.

## Install pip
1. `$ wget https://bootstrap.pypa.io/get-pip.py `
2. `$ sudo python3 get-pip.py`
3. `$ rm get-pip.py`
4. `$ sudo pip3 install virtualenv virtualenvwrapper`

## virtualenv and virtualenvwrapper setup
1. `$ nano .bashrc` and add the following 3 lines to bottom
```
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Exit out of the `.bashrc` file and run at the command line

2. `$ source .bashrc`

Create a new virtualenv called 'cv'

3. `$ mkvirtualenv cv`

# OpenCV Setup
When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

Install OpenCV (+ dependencies) and imutils
1. `(cv) $ pip install opencv-python`
2. `(cv) $ sudo apt update && sudo apt upgrade`
3. `(cv) $ sudo apt install -y libsm6 libxext6`
4. `(cv) $ sudo apt install -y libxrender-dev`
5. `(cv) $ pip install imutils`
6. `(cv) $ pip install influxdb`

# Other Libraries
## [Circuit Python](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)

1. `(cv) $ pip install --upgrade setuptools`
2. `(cv) $ pip install RPI.GPIO==0.6.3`
3. `(cv) $ pip install adafruit-blinka`

## [DHT Sensor](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated)
1. `(cv) $ git clone https://github.com/adafruit/Adafruit_Python_DHT.git`
2. `(cv) $ sudo apt-get update && sudo apt-get install build-essential python-dev python-openssl`
3. `(cv) $ cd Adafruit_Python_DHT/`
4. `(cv) $ python setup.py install`
5. `(cv) $ cd .. && rm -r Adafruit_Python_DHT/`

## [SGP30](https://learn.adafruit.com/adafruit-sgp30-gas-tvoc-eco2-mox-sensor/circuitpython-wiring-test)
1. `(cv) $ pip install adafruit-circuitpython-sgp30`

## VL53L1X
1. `(cv) $ pip install VL53L1X==0.0.2`

Check out [this post](https://github.com/pimoroni/vl53l1x-python/commit/8e8a29e19c4965219eff5baac085f49502503045) and change code to match accordingly.  If all steps have been followed correctly, code should be in:

`/home/pi/.virtualenvs/cv/lib/python3.5/site-packages/VL53L1X.py`

type:
`$ sudo nano home/pi/.virtualenvs/cv/lib/python3.5/site-packages/VL53L1X.py`

## [I2S Microphone](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-and-test)

Deactivate your virtualenv `(cv) $ deactivate`

1. `$ sudo nano /boot/config.txt` -- Uncomment #dtparam=i2s=on
2. `$ sudo nano /etc/modules` -- Add `snd-bcm2835` on its own line
3. `$ sudo reboot`
4. `$ lsmod | grep snd`
5. `$ sudo apt-get install git bc libncurses5-dev`
6. `$ sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source`
7. `$ sudo chmod +x /usr/bin/rpi-source`
8. `$ /usr/bin/rpi-source -q --tag-update`
9. `$ rpi-source --skip-gcc`
10. `$ sudo mount -t debugfs debugs /sys/kernel/debug` -- This may already be done and will say - mount: debugs is already mounted  - 
11. Make sure the module name is: 3f203000.i2s  by typing `$ sudo cat /sys/kernel/debug/asoc/platforms`
12. `$ git clone https://github.com/PaulCreaser/rpi-i2s-audio`
13. `$ d rpi-i2s-audio`
14. `$ make -C /lib/modules/$(uname -r )/build M=$(pwd) modules`
15. `$ sudo insmod my_loader.ko`
16. Verify that the module was loaded: `$ lsmod | grep my_loader` -> `$ dmesg | tail`
17. Set to autoload on startup:
18. `$ sudo cp my_loader.ko /lib/modules/$(uname -r)`
19. `$ echo 'my_loader' | sudo tee --append /etc/modules > /dev/null`
20. `$ sudo depmod -a`
21. `$ sudo modprobe my_loader`
22. `$ sudo reboot`


## PyAudio
1. `(cv) $ sudo apt-get install portaudio19-dev`
2. `(cv) $ sudo pip install PyAudio==0.2.11`

## Others
1. `(cv) $ pip install circuitpython-build-tools==1.1.5`
2. `(cv) $ pip install smbus2==0.2.1`

# Other things:
### 1. Configure Github on pi:
1. `$ mkdir /home/pi/Github`
2. `$ cd /home/pi/Github`
3. `$ git init`
4. `$ git remote add origin https://github.com/corymosiman12/ARPA-E-Sensor`
5. `$ git fetch origin`
6. `(cv) $ git checkout img_client_side`

You will need to add in your credentials to the git manager to pull from Github.  Hannah or Maggie this could be either of yours.




### 3. Set Cradlepoint as preferred network and set priority
Need to add cradlepoint network to pi and make sure it is `preferred`.
- Can just do this throught the pi GUI
- To ensure on boot that it joins correct network, edit: `$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`, and set priority as follows:

```
network={
    ssid = "cradlepoint_net"
    key_mgmt=NONE
    priority = 1
}
```


 Then, make sure that the cradlepoint network is at top priority (i.e. it will join it first out of all other networks) by editing:
 `$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`.  It should resemble:

```
network={
ssid="IBR600B-3f4"
psk="443163f4"
priority=1
key_mgmt=WPA-PSK
}
```

`$ sudo reboot` Check that it has joined the CP network.


### 4.
SSH from Antlet to pi atleast 1x. Upon SSH, you will enable trust between antlet and pi, and will therefore be able to use the `pysftp` library.



# Update 10/28/18 for SD cards already formatted 
Hannah - apologies, I made a mistake in the previous stuff.  On the SD cards you have gone through the above steps already, I need you to do the following.

1. `$ workon cv`
2. `(cv) $ pip uninstall board` (agree to removal)
3. `(cv) $ pip uninstall adafruit-blinka` (agree to removal)
4. `(cv) $ pip install adafruit-blinka`

I have changed this in the install instructions now (removed from the `Others` section above), so you can now follow those instructions exactly.