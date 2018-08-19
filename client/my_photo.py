import cv2
from datetime import datetime
import os
import pickle
import logging
import time
import threading
from imutils.video import WebcamVideoStream
import imutils

# TODO:
# 1. Add error checking and logging to script
# 2. Make sure script works when connected over local wLAN through linksys router

# Initialize camera.  The pi uv4l server must be running at the defined IP address
# and port number specified below.  The path: /stream/video.mjpeg can be found in the 
# pi's 192.168.0.4:8080/info

# logging.basicConfig(filename = 'client_logfile.log', level = logging.DEBUG,
#                     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#                     datefmt='%d-%m-%Y:%H:%M:%S',)

class MyPhoto2(threading.Thread):
    def __init__(self, img_dir, pi_ip_address, stream_type, sec):
        threading.Thread.__init__(self)
        self.img_dir = img_dir
        self.pi_ip_address = pi_ip_address
        self.stream_type = stream_type
        self.sec = sec
        self.video_status = False
        self.connect_to_video()
        self.start()
            
    def connect_to_video(self):
        if self.stream_type == "mjpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.mjpeg"
        elif self.stream_type == "h264":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.h264"
        elif self.stream_type == "jpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.jpeg"
        
        self.cam = WebcamVideoStream(stream_path).start()
        while not self.cam.stream.isOpened():
            print("Unsuccessful connection for self.sec = {}".format(self.sec))
            self.cam = WebcamVideoStream(stream_path).start()
            self.video_status = False
            time.sleep(1)
        self.video_status = True
        print("Connected for self.sec = {}".format(self.sec))

    def run(self):
        while 1:
            if datetime.now().second % 2 == self.sec:
                # print("Capturing image for second == {}".format(datetime.now().second))
                # logging.DEBUG("Capturing image for second == {}".format(sec))
                fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
                img = self.cam.read()
                # fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
                
                try:
                    # Convert image to greyscale
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                    # Write to disk
                    cv2.imwrite(os.path.join(self.img_dir,fname), img)
                except Exception as e:
                    print("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
                    # logging.CRITICAL("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
            
            # elif not capture_status:
            #     print("Capture from pi failed for second: {}".format(self.sec))
            #     print("Reconnecting to server")
            #     self.video_status = False
            #     self.connect_to_video()
            #     # logging.CRITICAL("Capture from pi failed for file: {}".format(fname))
            # time.sleep(0.99999)

#####################################################################################
##################################### LEFTOVERS #####################################
"""
class MyPhoto(threading.Thread):
    def __init__(self, img_dir, pi_ip_address, stream_type, sec):
        threading.Thread.__init__(self)
        self.img_dir = img_dir
        self.pi_ip_address = pi_ip_address
        self.stream_type = stream_type
        self.sec = sec
        self.video_status = False
        self.connect_to_video()
        self.start()
            
    def connect_to_video(self):
        if self.stream_type == "mjpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.mjpeg"
        elif self.stream_type == "h264":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.h264"
        elif self.stream_type == "jpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.jpeg"
        self.cam = cv2.VideoCapture(stream_path)
        while not self.cam.isOpened():
            print("Unsuccessful connection for self.sec = {}".format(self.sec))
            self.cam = cv2.VideoCapture(stream_path)
            self.video_status = False
            time.sleep(1)
        self.video_status = True
        print("Connected for self.sec = {}".format(self.sec))

    def run(self):
        while 1:
            if datetime.now().second % 2 == self.sec:
                # print("Capturing image for second == {}".format(datetime.now().second))
                # logging.DEBUG("Capturing image for second == {}".format(sec))
                fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
                capture_status, img = self.cam.read()
                # fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
                
                # if frame captured without errors
                if capture_status:
                    try:
                        # Convert image to greyscale
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                        # Write to disk
                        cv2.imwrite(os.path.join(self.img_dir,fname), img)
                    except Exception as e:
                        print("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
                        # logging.CRITICAL("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
                
                elif not capture_status:
                    print("Capture from pi failed for second: {}".format(self.sec))
                    print("Reconnecting to server")
                    self.video_status = False
                    self.connect_to_video()
                    # logging.CRITICAL("Capture from pi failed for file: {}".format(fname))
                time.sleep(0.99999)
"""
    # def valid_second(self):
    #     latest = self.sec_list[-1] + 2
    #     while latest < 60:
    #         self.sec_list.append(latest)
    #         latest += 2
    #     print(self.sec_list)

# def capture_photo_from_pi(img_dir, pi_ip_address, sec):
#     print("Thread started for video capture second == {}".format(sec))
#     # logging.DEBUG("Thread started for video capture second == {}".format(sec))
#     stream_path = "http://" + pi_ip_address + ":8080/stream/video.mjpeg"
#     try:
#         cam = VideoCapture(stream_path)
#     except Exception:
#         exit()

#     # Run infinitely
#     while 1:
#         if datetime.now().second == sec:
#             print("Capturing image for second == {}".format(sec))
#             # logging.DEBUG("Capturing image for second == {}".format(sec))
#             s, img = cam.read()
#             fname = datetime.now().strftime("%Y-%m-%d %H%M%S_grey.png")
            
#             # if frame captured without errors
#             if s:
#                 try:
#                     # Convert image to greyscale
#                     img = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY)

#                     # Write to disk
#                     imwrite(os.path.join(img_dir,fname), img)
#                 except Exception as e:
#                     print("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
#                     # logging.CRITICAL("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))
            
#             elif not s:
#                 print("Capture from pi failed for file: {}".format(fname))
#                 # logging.CRITICAL("Capture from pi failed for file: {}".format(fname))
#             time.sleep(1)