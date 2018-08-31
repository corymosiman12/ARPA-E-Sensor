#!/bin/bash
# Shell script to run inside Debian Antlet. Will install nano, curl, influxdb and dependencies.
# It will then start the influx service
apt-get update -y
apt-get install nano apt-transport-https ca-certificates curl -y
curl -sL https://repos.influxdata.com/influxdb.key | apt-key add -
source /etc/os-release
test $VERSION_ID = "7" && echo "deb https://repos.influxdata.com/debian wheezy stable" | tee /etc/apt/sources.list.d/influxdb.list
test $VERSION_ID = "8" && echo "deb https://repos.influxdata.com/debian jessie stable" | tee /etc/apt/sources.list.d/influxdb.list
test $VERSION_ID = "9" && echo "deb https://repos.influxdata.com/debian stretch stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update && apt-get install influxdb
service influxdb start
