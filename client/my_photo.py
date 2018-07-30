from cv2 import *
from datetime import datetime
import os
import pickle
import logging

# TODO:
# 1. Add error checking and logging to script
# 2. Make sure script works when connected over local wLAN through linksys router


# Initialize camera.  The pi uv4l server must be running at the defined IP address
# and port number specified below.  The path: /stream/video.mjpeg can be found in the 
# pi's 192.168.0.4:8080/info

def capture_photo_from_pi(base_path, pi_ip_address, pi_id):
    path = os.path.join(base_path, pi_id)
    stream_path = "http://" + pi_ip_address + ":8080/stream/video.mjpeg"
    cam = VideoCapture(stream_path)

    # Run infinitely
    while 1:
        s, img = cam.read()
        fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
        
        # if frame captured without errors
        if s:
            try:
                # Convert image to greyscale
                img = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY)

                # Write to disk
                imwrite(os.path.join(path,fname), img)
            except Exception as e:
                logging.CRITICAL("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
        
        elif not s:
            logging.CRITICAL("Capture from pi failed for file: {}".format(fname))
    