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
import my_utils

logging.basicConfig(filename = 'client_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

class MyClient():
    def __init__(self, server_id):
        self.server_id = server_id
        self.conf = self.import_conf(self.server_id)
        self.server_ip = self.conf[self.server_id]
        self.root = self.conf['root']
        self.stream_type = self.conf['stream_type']
        self.listen_port = int(self.conf['listen_port'])
        self.influx_client = influxdb.InfluxDBClient('localhost', 8086, database='hpd_mobile_test')

    def import_conf(self, server_id):
        with open('client.conf', 'r') as f:
            conf = json.loads(f.read())
            
        return conf

    def create_message(self, params):
        # Always include the datetime as the first line item in
        # a message sent to the server
        dt_str = [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]
        for p in params:
            dt_str.append(p)
        
        message = '\r\n'.join(dt_str)
        print("Sending Message: \n{}".format(message))
        return message.encode()

    def my_recv_all(self, s, timeout=2):
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
        json_body = []
        for r in self.response["Readings"]:
            json_body.append({
                "measurement": "environmental_params",
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
        # print("Successful Write: {}".format(successful_write))

    def get_sensors_data(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.listen_port))
        s.sendall(self.create_message(["sensors"]))
        self.response = json.loads(my_utils.my_recv_all(s))
        try:
            successful_write = self.influx_write()        
        s.close()


if __name__ == "__main__":
    """
    The client must be run by specifying a server id. Example:
        client$ python client.py S1
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


