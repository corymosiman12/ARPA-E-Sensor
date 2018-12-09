# Intro
A service basically allows us to run a script immediately on boot without having to enter any commands.

We will want to make sure that the services work on all of the Pi's, but we need to disable them until we are ready to deploy.  This eliminates the service from running (collecting data) when we aren't testing / depoloying.  SO, after we go through the following, make sure to run `sudo systemctl disable hpd_mobile.service`, which will prevent it from starting on boot.

# Server Side
1. On the pi, run the following to create a new file: `$ sudo touch /lib/systemd/system/hpd_mobile.service`.  Edit that file by running `$ sudo nano /lib/systemd/system/hpd_mobile.service` and add the following:

```
[Unit]
Description=Serice to start Github/server/server.py on boot from venv
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/pi/.virtualenvs/cv/bin/python /home/pi/Github/server/server.py
restart=always

[Install]
WantedBy=multi-user.target
```

2. Reload service daemon: `$ sudo systemctl daemon-reload`
3. Enable the service by default: `$ sudo systemctl enable hpd_mobile.service`
4. Reboot the pi: `$ sudo reboot`
5. Check if the service is running: `$ sudo systemctl status hpd_mobile.service`

# Antlet Side
Basically will do the exact same thing, just with the requirements for the client application (notice we add a line to sleep the service for 60 seconds before the service actually starts.  This is just to give the pi's time to basically have a minute or two of data before the Antlets begin to ask for data).  Additionally , make sure to replace [server_id] with BS3 or whatever is the id of the server this antlet is connecting to:
1. `$ sudo touch /lib/systemd/system/hpd_mobile.service`
2. `$ sudo nano /lib/systemd/system/hpd_mobile.service` and add the following:

```
[Unit]
Description=Serice to start Github/client/client.py on boot from venv
After=multi-user.target

[Service]
Type=idle
ExecStart=/root/.virtualenvs/cv/bin/python /root/client/client.py [server_id]
restart=always

[Install]
WantedBy=multi-user.target
```

2. Reload service daemon: `$ sudo systemctl daemon-reload`
3. Enable the service by default: `$ sudo systemctl enable hpd_mobile.service`
4. Reboot the pi: `$ sudo reboot`
5. Check if the service is running: `$ sudo systemctl status hpd_mobile.service`

## Extras
Stop service: `$ sudo systemctl stop [my_service].service`
Start service: `$ sudo systemctl start [my_service].service`