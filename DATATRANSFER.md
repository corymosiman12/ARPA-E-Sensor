# General
- Make sure hpd_mobile.service is stopped on all antlets and pis.
- I created a network bridge for each of the Antlets.  You can now ssh directly from your computer to the antlet. They were given IP addresses in the CP router in the 192.168.0.20x range (HPD Black)and 192.168.0.21x (HPD Red)  Their hostnames were also changed:

### HPD Black
```
hostname        ip address
BS1-Antlet      192.168.0.201
BS2-Antlet      192.168.0.202
BS3-Antlet      192.168.0.203
BS4-Antlet      192.168.0.204
BS5-Antlet      192.168.0.205
```
- You can ssh into each antlet via: `$ ssh root@BS1-Antlet` or `$ ssh root@192.168.0.201`


# Photos, Audio, Logfiles
  
- Make sure hpd_mobile.service is stopped on all antlets and pis: <br />
    `sudo systemctl stop hpd_mobile.service` <br />
    `sudo systemctl disable hpd_mobile.service`
- Move sensor log file from pi to antlet via sftp:<br />
    `sftp pi@192.168.0.10x:/home/pi/sensors_logfile.log /root/`
- Plug external HD into the antsle in one of the blue ports (USB3.0)
- Stop antlet in antman and [enable USB pass through](https://docs.antsle.com/usbdrives/#usb-pass-through). Restart antlet
- SSH into the antlet
- Find connected devices with: <br />
- `sudo fdisk -l` or `lsblk`
- Mount drive with:<br />
     `sudo mount /dev/sda2 /media/externalHD`
- Create subfolder for specific test (only once per test):<br />
    `mkdir /media/externalHD/testxx`
- Move files to external HD:<br />
    `mv /mnt/vdb/BSx /media/externalHD/testxx/`
- Get the logfiles: <br />
    `mv /root/client_logfile.log /media/externalHD/testxx/BSx`<br />
    `mv /root/sensors_logfile.log /media/externalHD/testxx/BSx`
- Unmount drive with: <br />
    `udisksctl unmount -b /dev/sda2`
- Detach with: <br />
    `udisksctl power-off -b /dev/sda2`
- Repeat this for all of the antlets

# Collecting InfluxDB (env_params)
To get all of the `env_params` data from the InfluxDB antsle, we will create a backup of the `hpd_mobile` influxdb database, and then restore it into an influx container on our machine.

## Create a backup of hpd_mobile
We tell the antsle which database we want backed up, since when, and where we want to save the backup.  We will do this first locally on the antlet, then transfer the backup to our external disk.

1. ssh into the `InfluxDB` antlet

2. Make a directory for where to store the backup: `$ mkdir testxx_influx`

3. Create the backup of the hpd_mobile database:
- `$ influxd backup -portable -database hpd_mobile test5_influx/`
- This makes a backup of the `hpd_mobile` database, and stores all info in the `test5_influx` directory created in step 2 above

4. Transfer it to the root Antsle (root@192.168.0.50 or root@hpdblack) by ssh'ing into this, then performing an sftp
- From a new terminal window: `$ ssh root@hpdblack`
- Transfer data into the root Antsle: `$ sftp -r 10.1.1.100:/root/test5_influx/ .`

5. Transfer from root Antsle to the external disk.
- From a new terminal window: `$ sftp -r -a root@hpdblack:/root/test5_influx/* /Volumes/HPD_Mobile/test5/influx`

## Create influx container on your computer
You must have docker installed on your computer for this to work.

1. Open up a new terminal and create a new docker container named `influx_xx`: <br />
`docker run -p 8088:8086 -v influx_xx:/var/lib/influxdb --name influx_xx influxdb:1.7`

2. Start the docker container: `docker container start influx_xx`

3. From a new terminal, access a bash terminal inside the `influx_xx` container: 
- `$ docker exec -it influx_xx bash`
- Create a new directory for the backup files: `$ mkdir testx_dir`

4. Copy the data from the external disk into the container filesystem:
- From a new terminal: `$ docker cp /Volumes/HPD_Mobile/test13/influx/. influx_xx:testx_dir`

5. Restore a new database in the docker container:
- From a new terminal, access a bash terminal inside the influxdb container: `$ docker exec -it influx_xx bash`
- Inside the influxdb bash shell: `$ influxd restore -portable -db hpd_mobile -newdb test_x /testx_fir`
- Access the influx CLI: `$ influx`
- At the influx CLI, change the timestamp display used from queries more user friendly format: `> precision rfc3339`
- Show the databases: `> show databases`

# InfluxDB Docker (Iowa)
You must have docker installed on your computer for this to work.

## Create an influx docker container
1. Open up a new terminal and create a new docker container: `$ docker run -p 8088:8086 -v influxdb3:/var/lib/influxdb --name influxdb3 influxdb:1.7`
- This creates a new container from the `influxdb` image version 1.7.  We need to have atleast v1.7
- This new container is named `influxdb3`.  Feel free to name whatever you want.
- This new container will store the database data in the `/var/lib/influxdb` directory inside the influxdb3 filesystem.
- It maps port 8088 on your local host to 8086 of the container.  By default, InfluxDB uses port 8086 as the HTTP API port.  This will be important later.  Any port on your localhost that is not in use can be mapped to port 8086 on the docker container.  For instance, I could just as easily done: `$ docker run -p 8086:8086 -v $influxdb3:/var/lib/influxdb --name influxdb3 influxdb`
- Start the docker container: `$ docker container start influxdb3`

## Restore the backup database
Once the influxdb container is running, copy the backup data from the external disk into the container filesystem.

1. From a new terminal, access a bash terminal inside the `influxdb` container: 
- `$ docker exec -it influxdb3 bash`
- Create a new directory for the backup files: `$ mkdir test5_influx`

2. Copy the data from the external disk into the container filesystem:
- From a new terminal: `$ docker cp /Volumes/HPD_Mobile/test5/influx/. influxdb3:test5_influx`

3. Restore a new database in the docker container:
- From a new terminal, access a bash terminal inside the influxdb container: `$ docker exec -it influxdb bash`
- Inside the influxdb bash shell: `$ influxd restore -portable -db hpd_mobile -newdb test5 /test5_influx`
- Access the influx CLI: `$ influx`
- At the influx CLI, change the timestamp display used from queries more user friendly format: `> precision rfc3339`
- Show the databases: `> show databases`

```
> show databases
name: databases
name
----
_internal
test5
```

# Access the data in Python
- See /ARPA-E-Sensor/infludb_python/HPD_Mobile Data Access and Plot Example.ipynb

## How to transfer via an indirect connection (if above method is not available)
- We want to write directly from antsle to the external disk (named `HPD_Mobile`), so connect the external disk to your computer
- We will want to mimic the file structure already being adhered to by all of the antsles for writing data.  Create a new directory on the `HPD_Mobile` external disk labeled `test5` (or similar, w.e. test you are on).  Then, within that, create a directory for each of the `BS1`, `BS2`, etc.
- Create a directory within the `test5` to store the InfluxDB backup (explained later).  So, you should have a directory structure on the external disk that looks like:

```
test5
    - BS1
    - BS2
    - BS3
    - BS4
    - BS5
    - influx
```

- Connect your computer to the hub
- Turn off wi-fi, connect to box, make sure you get an IP address.  Just allow this to happen over DHCP, shouldn't need to assign yourself a static IP address
- Now we will begin transferring data via `sftp` from each Antlet directly onto the external disk. 
- We will perform multiple sftp data transfers at the same time. The following paths follow the mounting structure for a mac
- We will transfer photos and audio data separately onto the external disk for each antlet.  You could even split this up by date if needed
- We tell sftp that we want to transfer from A -> B, where A is the location on the antlet, and B is the location on the external disk.  The -r means recursive and the -a option attempts to continue interrupted transfers and only overwrites a file if there are differences in the file (this is just a safety precaution).
- Transfer audio from BS1 to external disk: 
    - `$ sftp -r -a root@192.168.0.201:/mnt/vdb/BS1/audio /Volumes/HPD_Mobile/test5/BS1/`
- Transfer images from BS1 to external disk: 
    - `$ sftp -r -a root@192.168.0.201:/mnt/vdb/BS1/img /Volumes/HPD_Mobile/test5/BS1/`
- Repeat this for all of the antlets
