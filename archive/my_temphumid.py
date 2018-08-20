from cv2 import * ###don't think we will need this
from datetime import datetime
import os
import pickle
import logging
import time

import sys ###not sure which libraries above are needed (I addded Adafruit_DHT and time)

import Adafruit_DHT

# Define which sensor we are using (DHT11 or DHT22)
sensor = Adafruit_DHT.DHT22 
# Define which GPIO pin the sensor is connected to
pin = 4
# How long to wait before taking new measurements, in seconds
timeDelay = 10


def capture_temp_humid_from_pi(base_path, pi_ip_address, pi_id):
    path = os.path.join(base_path, pi_id)

    # Run infintely
    while 1:
        humidity, temperature_C = Adafruit_DHT.read_retry(sensor, pin)
        # Convert Celcius temperature to Fahrenheit
        temperature_F = temperature_C * 9/5.0 + 32
        # Choose which to report 
        temperature = temperature_F
        #temperature = temperature_C

        fname = datetime.now().strftime("%Y-%m-%d %H%M%S_TempHumid.txt") 
        ###not sure what file type is best. Also this creates a new file for every reading,
        ###but not sure if we want to append to 1 file (or 1 per day?)

        # Check that both captured without errors
        if humidity and temperature: 
            try:
                # Open new file we just made and write data to it    
                file = open(fname, "w")
                file.write(humidity + " " + temperature)
                file.close()
            except Exception as e:
                logging.CRITICAL("Unable to take reading and write to disk. Error: {}. File: {}".format(e,fname))    
        elif not temperature and humidity: ###not sure if this is correct way to state this
            logging.CRITICAL("Capture from pi failed for file: {}".format(fname))
        # Only try to take a reading every 10 seconds
        time.sleep(timeDelay)    


