import my_photo
import json
import socket
import sys
import os
from datetime import datetime
import threading
import logging
import time
import influxdb

logging.basicConfig(filename = 'client_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

class MyClient():
    def __init__(self, server_id):
        self.server_id = server_id
        self.conf = self.import_conf(self.server_id)
        self.server_ip = self.conf['servers'][self.server_id]
        self.root = self.conf['root']
        self.image_dir = os.path.join(self.root, 'img')
        self.stream_type = self.conf['stream_type']
        self.listen_port = int(self.conf['listen_port'])
        self.influx_client = influxdb.InfluxDBClient('localhost', 8086, database='hpd_mobile_test')
        self.create_img_dir()
        self.photos = my_photo.MyPhoto2(self.image_dir, self.server_ip, self.stream_type)

    def import_conf(self, server_id):
        """
        Import the client configuration file.

        param: server_id <class 'str'>
        return: <class 'dict'> of configuration parameters
        """
        with open('client.conf', 'r') as f:
            conf = json.loads(f.read())
            
        return conf
    
    def create_img_dir(self):
        """
        Check if server directories for images exist.  If they exist, do nothing.
        If they don't exist yet, create.  Image directories will be created like:
            root/img/S1/datetime
            ...
            root/img/Sn/datetime
        """
        self.image_dir = os.path.join(self.root, 'img',self.server_id)
        if not os.path.isdir(self.image_dir):
            os.makedirs(self.image_dir)

    def create_message(self, to_send):
        """
        Configure the message to send to the server.
        Elements are separated by a carriage return and newline.
        The first line is always the datetime of client request.

        param: to_send <class 'list'>
                List of elements to send to server.

        return: <class 'bytes'> a byte string (b''), ready to 
                send over a socket connection
        """
        dt_str = [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]
        for item in to_send:
            dt_str.append(item)
        
        message = '\r\n'.join(dt_str)
        print("Sending Message: \n{}".format(message))
        return message.encode()

    def my_recv_all(self, s, timeout=2):
        """
        Regardless of message size, ensure that entire message is received
        from server.  Timeout specifies time to wait for additional socket
        stream.

        param: s <class 'socket.socket'>
                A socket connection to server.
        return: <class 'str'>
                A string containing all info sent.
        """
        #make socket non blocking
        s.setblocking(0)
        
        #total data partwise in an array
        total_data=[]
        data=''
        
        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break
            
            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break
            
            #recv something
            try:
                data = s.recv(8192).decode()
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin = time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass
        
        #join all parts to make final string
        return ''.join(total_data)

    def influx_write(self):
        """
        Format all data received from server to be inserted into the
        InfluxDB.  This is currently specific to all data excluding
        microphone and camera data.

        return: <class 'bool'>
                When the influx write_points method is called to write
                all points of the json_body to the DB, the result of the
                write (True or False) indicates success or not.  This
                is returned for further processing.
        """
        json_body = []
        for r in self.response["Readings"]:
            json_body.append({
                "measurement": "env_params",
                "tags": {
                    "server_id": self.server_id,
                    "server_ip": self.server_ip,
                    "client_request_time": self.response["Client_Request_Time"],
                    "server_response_time": self.response["Server_Response_Time"]
                },
                "time": r["time"],
                "fields": {
                    "light_lux": int(r["light_lux"]),
                    "temp_f": int(r["temp_f"]),
                    "rh_percent": int(r["rh"]),
                    "dist_inches": int(r["dist_in"]),
                    "co2eq_ppm": int(r["co2eq_ppm"]),
                    "tvoc_ppb": int(r["tvoc_ppb"]),
                    "co2eq_base_ppm": int(r["co2eq_base_ppm"]),
                    "tvoc_base": int(r["tvoc_base"])
                }
            })
        return(self.influx_client.write_points(json_body))

    def get_sensors_data(self):
        """
        Connect to server and get data.  This is currently specific to
        all data excluding the microphone and camera.
        """
        # Instantiate IPV4 TCP socket class
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create a socket connection to the server at the specified port
        s.connect((self.server_ip, self.listen_port))

        # Send message over socket connection, requesting aforementioned data
        s.sendall(self.create_message(["env_params"]))

        # Receive all data from server.  Load as dictionary
        self.response = json.loads(self.my_recv_all(s))
        
        # Attempt to write to InfluxDB.  Relay success/not to server
        # Upon success, server removes data from cache
        try:
            # influx_write() returns 'bool'
            successful_write = self.influx_write()
            if successful_write:
                s.sendall(self.create_message(["SUCCESS"]))
            else:
                s.sendall(self.create_message(["NOT SUCCESS"]))
        except:
            s.sendall(self.create_message(["NOT SUCCESS"]))

        # Check that server received message correctly
        self.validation = self.my_recv_all(s)
        print("Validation: {}".format(self.validation))

        # Close socket
        s.close()


if __name__ == "__main__":
    """
    The client must be run by specifying a server id. Example:
        client$ python client.py S1
    Client is currently set to ping it's specified server
    every 2 minutes, get data, and write to InfluxDB.
    
    TODO: Get camera working as well.
    """
    server_id = sys.argv[1]

    # Define directory for saving photos
    # img_dir = os.path.join(ext_root, server_id, "data", "img")
    c = MyClient(server_id)

    while True:
        if datetime.now().minute % 2 == 0:
            time.sleep(2)
            c.get_sensors_data()
            time.sleep(60)
    # print(img_dir)
    # print(stream_type)
    
    # vid_even = my_photo.MyPhoto2(img_dir, pi_ip_address, stream_type, 0)
    # vid_odd = my_photo.MyPhoto2(img_dir, pi_ip_address, stream_type, 1)


#####################################################################################
##################################### LEFTOVERS #####################################
# Obtain server ip address and external drive root directory for saving data
# pi_ip_address, ext_root, stream_type, listen_port = import_conf('client.conf', server_id)
# sudo service uv4l_raspicam restart
# sudo nano /etc/uv4l/uv4l-raspicam.conf
# interface eth0
# static ip_address=192.168.0.3
# static routers=192.168.0.1
# static domain_name_servers=192.168.0.1


