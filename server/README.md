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