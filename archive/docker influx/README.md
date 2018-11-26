# General
This IS NOT used in the final setup of the HPD Mobile, but is kept as reference to create an InfluxDB instance in a docker container.

This wiki is meant to describe the setup of the InfluxDB docker container.  All commands must be run from the `ARPA-E-Sensor/docker influx/` directory (where this file is currently located).  Docker must be installed on the machine for this to work.

# Steps
Open up a new terminal window.  Navigate to the `ARPA-E-Sensor/docker influx/` directory.  Create empty container file for InfluxDB:
- `$ docker run --rm influxdb influxd config > influxdb.conf`

Build the container (Executes the Docker file in the directory):  
- `$ docker build -t influxdb .`

Start the container, name it `influxdb`, and have it run on port `8086` on your local host:
- `$ docker run --name=influxdb -d -p 8086:8086 influxdb`

This exposes port 8086 of your localhost to the indfluxdb container (basically, forwarding port 8086 from localhost to the container).  Check that the container is running:
- `$ docker ps -a`

To access a bash shell in the influxdb container:
- `$ docker exec -it influxdb 'bash'`

To access the influx CLI once in a bash shell, simply run `influx`.  An intro to the influx CLI can be found [here](https://docs.influxdata.com/influxdb/v1.6/tools/shell/)

# Extra tips
From the influx CLI, show the available databases:
- `> SHOW databases`

Create a database for our project:
- `> CREATE DATABASE hpd_mobile`

Use the database at the CLI. Allows for direct querying / insertion of data.  More helpful when you actually begin to query the database / check that data is being written correctly:
- `> USE hpd_mobile`