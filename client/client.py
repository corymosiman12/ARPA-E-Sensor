import my_photo
import json
import socket
import sys
import os
from datetime import datetime
import threading
import logging
import time

logging.basicConfig(filename = 'client_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

def import_conf(config_file, server_id):
    with open(config_file, 'r') as f:
        conf = [line.strip('\n') for line in f if server_id in line 
                or ('root' in line and not '#' in line) 
                or ("stream" in line and not '#' in line)]
        # print(conf)
        assert len(conf) == 3
        return((conf[0].split(" ")[1], conf[1].split(" ")[1], conf[2].split(" ")[1]))

def create_message(params):
    """
    Join all parameters with a carriage return and newline and
    send to server. The default parameters are:
        1. datetime as a str()
        2. temp
        3. rh
        4. ...ELSE...
    """
    # Always include the datetime as the first line item in
    # a message sent to the server
    dt_str = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    for p in params:
        dt_str.append(p)
    params = '\r\n'.join(params)
    print(params)

def get_data(server_ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # test_file = "/Users/corymosiman/Dropbox/ARPA-E SENSOR Project Folder/3 Tasks/1 HPDmobile/Documents/secondPurchaseDiagram.pdf"
    with open(test_file, 'rb') as f:
        a = f.read()
    print(a)
    print(len(a))
    s.connect((server_ip, 1025))
    s.sendall(create_message())
    echo = s.recv(4096).decode()
    print(echo)
    print(len(echo))
    s.close()

if __name__ == "__main__":
    """
    The client must be run by specifying a server id. Example:
        client$ python client.py S1
    """
    server_id = sys.argv[1]

    # Obtain server ip address and external drive root directory for saving data
    pi_ip_address, ext_root, stream_type = import_conf('client.conf', server_id)

    # Define directory for saving photos
    img_dir = os.path.join(ext_root, server_id, "data", "img")
    # print(img_dir)
    # print(stream_type)
    
    # vid_even = my_photo.MyPhoto(img_dir, pi_ip_address, stream_type, 0)
    vid_even = my_photo.MyPhoto2(img_dir, pi_ip_address, stream_type, 0)
    vid_odd = my_photo.MyPhoto2(img_dir, pi_ip_address, stream_type, 1)


# sudo service uv4l_raspicam restart
# sudo nano /etc/uv4l/uv4l-raspicam.conf
# interface eth0
# static ip_address=192.168.0.3
# static routers=192.168.0.1
# static domain_name_servers=192.168.0.1


