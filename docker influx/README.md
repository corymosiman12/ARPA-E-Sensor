This IS NOT used in the final setup of the HPD Mobile, but is kept as reference.

This wiki is meant to describe the setup of the InfluxDB docker container.  All commands must be run from the `docker influx` directory.  Docker must be installed on the machine to follow this wiki.

Create empty container file for InfluxDB:

`docker run --rm influxdb influxd config > influxdb.conf`

Build the container (Executes the Docker file in the directory):  

`docker build -t influxdb .`

Start the container:

`docker run --name=influxdb -d -p 8086:8086 influxdb`

This exposes port 8086 of your localhost to the indfluxdb container (basically, forwarding port 8086 from localhost to the container).

Check that the container is running:

`docker ps -a`

To access a bash shell in the influxdb container:

`docker exec -it influxdb 'bash'`

To access the influx CLI once in a bash shell, simply run `influx`.  An intro to the influx CLI can be found [here](https://docs.influxdata.com/influxdb/v1.6/tools/shell/)

From the influx CLI, show the available databases:

`>SHOW databases`

Create a database for our project:

`>CREATE DATABASE hpd_mobile`

Use the database at the CLI. Allows for direct querying / insertion of data.  More helpful when you actually begin to query the database / check that data is being written correctly:

`>USE hpd_mobile`

# Backups
After data collection has completed, we need to take a backup of the InfluxDB, move it off the Antsle, make sure we can recover it.

This information can also be found [here](https://docs.influxdata.com/influxdb/v1.6/administration/backup_and_restore/)

Create a backup of the `hpd_mobile` database, get to the docker CLI.  Create a new directory to store all of the data:

`>mkdir hpd_mobile_backup`

The syntax for the backup command is: `influxd backup -database [database name] [backup directory]`.  So, for our above scenario:

`>influxd backup -database  hpd_mobile /hpd_mobile_backup`

We can now copy this out of the docker container.  Exit out of the docker CLI and just use a terminal on your host.  Assuming the path where we want to move the backup files to on our local host is `~/my_backups`, and the database was backed up to , run the following:

`docker container cp influxdb:hpd_mobile_backup/ ~/my_backups/`