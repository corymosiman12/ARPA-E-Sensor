This repository contains both the client and server side code for the ARPA-E-Sensor project HPDMobile.  Each server is a raspberry pi with the following peripherals:
- Raspberry pi camera
- SPG30 Gas Sensor (TVOC and eCO2)
- DHT22 Sensor (Temp and RH)
- SPH0645LM4H Microphone
- VL53L1X Distance Sensor (meters)
- APDS-9301 Sensor (lux)

Raspberry pi must be running Stretch OS.  Both the camera and I2C must be enabled.  The UV4L Streaming Server module must be running, follow steps [here](https://github.com/corymosiman12/ARPA-E-Sensor/wiki/Setting-up-the-Pi's).

All data besides images will be stored in an InfluxDB database running in a docker container on the client (port: 8086).  See the wiki page `InfluxDB Setup` for configuration of InfluxDB.  InfluxDB is a time-series database.  Although not explicit, it still basically uses the concept of tables.  We will have two 'tables', one called `env_params` and the other `audio`.

# env_params table
The servers will collect data (everything except audio and photos) at a specified `read_interval` (server.conf), timestamp the data, and store it in memory.  They listen on a specific port `listen_port`, waiting for the client to request data.  Upon request, data will be transferred over a TCP socket.  If the client successfully receives and writes the data to the InfluxDB, the server will clear those readings from memory and begin collecting for the next interval.

# audio table
The microphones will collect 1 second worth of data at 32,000 sps, and will then perform an fft analysis on them.  