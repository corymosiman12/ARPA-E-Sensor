# Intro
This page is meant to describe the process for getting the UV4L library up and running on a Raspberry Pi.  UV4L allows the pi to act as a streaming video server, which can be connected to using `OpenCV` on a client side application.

1. The pi must be running the `stretch` OS (didn't work when I tried on `jessie`).  Type `$ cat /etc/os-release` to check OS version.  If not, follow the guide [here](https://www.raspberrypi.org/documentation/installation/noobs.md).
2. The camera must be enabled on the pi.  Run `$ sudo raspi-config`, then go to `Interfacing Options` and enable.
3. We also want to enable `ssh`, so do that in the same `Interfacing Options` as well.
4. TODO = **What else do we need to enable: SPI, I2C, Serial, etc. ...**
3. For the most part, this wiki will follow the install [here](https://www.linux-projects.org/uv4l/installation/).  I have condensed it to only the commands we need below.  This will require an internet connection on the pi.

# UV4L on the Pi
Open a terminal and type:
`$ curl http://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -`

Add the following line to the end of the file `/etc/apt/sources.list` by typing `$ nano /etc/apt/sources.list` at the command line:
`deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main`

Next, update, fetch, and install uv4l packages:
`$ sudo apt-get update`
`$ sudo apt-get install uv4l uv4l-raspicam`

We want the driver to load at boot, so type the following
`$ sudo apt-get install uv4l-raspicam-extras`

Install the front-end server:
`$ sudo apt-get install uv4l-server uv4l-uvc uv4l-xscreen uv4l-mjpegstream uv4l-dummy uv4l-raspidisp`

Reboot the pi.  By default, the streaming video server will run on port 8080.  You should now be able to access the video server from a web-browser by typing in `localhost:8080`.  Clicking on the MJPEG/Stills stream will show you the stream.  The `Control Panel` tab will allow you to adjust settings.  I found that reducing the resolution to 3x our target (112x112 is target of WISPCam), so 336x336, gives us minimal lag time.

## Raspicam Options
Edit the raspicam default options to use a lower resolution and framerate and use mjpeg streaming.  Set the resolution to 336x336 and the framerate to 2fps.  This is done via:
`$ sudo nano /etc/uv4l/uv4l-raspicam.conf`

Find the section labeled `raspicam driver options`.  In this section, modify :
encoding = mjpeg
width = 336
height = 336
framerate = 2

Restart the UV4L server, and you should see these defaults change.  This command can be run at anytime to restart the UV4L server.
`$ sudo service uv4l_raspicam restart`

## Streaming Over the Network
Now, to test the pi running over the network:
1. Connect the pi to on our network.
2. Check the IP address of the pi using `$ ifconfig`.
3. Connect your computer to the same network, and access at the browser through: `[piIpAddress]:8080`, i.e. `192.168.1.104:8080`.  You should now have the same stuff available as if you were accessing it through the localhost.

# OpenCV Setup
## 1. Easiest Method
This is a combination of the update posted in [this install guide](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961), addressing the [errors noted here](https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo).  Note that parts 1 and 2 are just to get the virtualenv setup.  Once we are in the virtualenv, it follows the first install guide.

1. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

2. virtualenv and virtualenvwrapper setup
`$ nano .bashrc` and add the following 3 lines to bottom
```
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

3. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

4. Install OpenCV (+ 3 dependencies), influxdb client, imutils
`(cv) $ pip install opencv-python`
`(cv) $ apt update && apt upgrade`
`(cv) $ apt install -y libsm6 libxext6`
`(cv) $ apt install -y libxrender-dev`
`(cv) $ pip install imutils`
`(cv) $ pip install influxdb`
`(cv) $ pip install pysftp`

# Other things:
1. Configure Github on pi:
`$ mkdir /home/pi/Github`
`$ cd /home/pi/Github`
`$ git init`
`$ git remote add origin https://github.com/corymosiman12/ARPA-E-Sensor`
`$ git pull origin master`

You will need to add in your credentials to the git manager to pull from Github.  Hannah or Maggie this could be either of yours.

2. Need to add cradlepoint network to pi and make sure it is `preferred`.
- Can just do this throught the pi GUI
- To ensure on boot that it joins correct network, edit: `$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`, and set priority as follows:
```
network={
    ssid = "cradlepoint_net"
    key_mgmt=NONE
    priority = 1
}
network={
   ...Don't care...
}
```

3. SSH from Antlet to pi atleast 1x. Upon SSH, you will enable trust between antlet and pi, and will therefore be able to use the `pysftp` library.

4. Likely missed things...