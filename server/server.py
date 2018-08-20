import socket
import threading
import os
import sys
import logging
from datetime import datetime
import json
import hpd_sensors
import time

# Set logging level and format logging entries.
"""
logging.basicConfig(filename = 'server_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)
"""
def import_server_conf():
    """
    This function is used to import the configuration file from the
    server directory.  The settings are saved as key:value pairs
    and returned.

    TODO: Format data as json, similar to client.py
    """
    try:
        with open('server.conf', 'r') as f:
            config_params = [line.strip('\n') for line in f if not "#" in line]
            settings = {}
            for setting in config_params:
                if setting != "":
                    k, v = setting.split(" ")
                    settings[k] = v
            return settings
    except:
        logging.CRITICAL("Unable to read server configuration file")
        print("Unable to read server configuration file")
        exit()

                                     
class Server():
    def __init__(self, settings):
        """
        The server class is the main class, and in this instance, the
        main thread that will be executed.  Once initialized,
        the listening socket is opened and created.

        param: settings <class 'dict'>
                    Contains a listen_port,
                    root document directory,
                    sensor read interval, ....
        """
        self.settings = settings
        self.host = ''
        self.port = int(self.settings['listen_port'])
        self.root = self.settings['root']
        self.sensors = hpd_sensors.Sensors(int(self.settings['read_interval']))
        self.sensors.start()
        self.create_socket()
        

    def create_socket(self):
        """
        Create a socket, listen, and wait for connections.  Upon acceptance
        of a new connection, a new thread class (Multiple) is spun off with
        the newly created socket.  The thread closes at the end of execution.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print("Listen socket created on port: {}".format(self.port))
        self.sock = sock
        while True:
            # accept() method creates a new socket separate from the
            # main listening socket.
            (client_socket, client_address) = self.sock.accept()
            if client_socket:
                thr = Multiple(client_socket, client_address, self.settings, self.sensors)
                thr.start()
                thr.join()
                print("New connection with: {}".format(client_address))

class Multiple(threading.Thread):
    """
    Instantiate a new thread to manage socket connection with client.
    A multi-threaded server approach likely is unnecessary, but, it's
    good practice.

    param: socket <class 'socket.socket'>
            A newly created socket created by the listen socket
            upon acceptance of new connection.
    param: address
            IP address of client to respond to
    param: settings <class 'dict'>
            Server configuration settings
    param: sensors <class 'hpd_sensors.Sensors'>
            Pointer to master class of sensors.  Allows thread
            to get readings from sensors to send to client.
    """
    def __init__(self, socket, address, settings, sensors):
        threading.Thread.__init__(self)
        self.client_socket = socket
        self.client_address = address
        self.stream_size = 4096
        self.settings = settings
        self.sensors = sensors
    
    def decode_request(self):
        """
        Each line in the client message is separated by a
        carriage return and newline. The first line is 
        the time the request is sent from the client side.  Additional
        lines specify if client wants env_params or audio data.
        """
        decoded = self.request.split('\r\n')
        self.client_request_time = decoded[0]
        self.client_request = decoded[1]
        
    def send_sensors(self):
        """
        Create dictionary of readings, along with additional meta data
        client_request_time and server_response_time, which may be useful 
        for debugging.  List of all readings is sent as the "Readings".

        return: <class 'bytes'>
                Encoded byte string ready to stream to client
        """
        to_send = {"Client_Request_Time": self.client_request_time,
                   "Server_Response_Time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "Readings": self.sensors.readings}
        return json.dumps(to_send).encode()

    def my_recv_all(self, timeout=2):
        """
        Regardless of message size, ensure that entire message is received
        from client.  Timeout specifies time to wait for additional socket
        stream.  By default, will use socket passed to thread.

        return: <class 'str'>
                A string containing all info sent.
        """
        #make socket non blocking
        self.client_socket.setblocking(0)
        
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
                data = self.client_socket.recv(8192).decode()
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
    
    def run(self):
        """
        Process client request, send requested information, and ensure
        data has been received and successfully written to disk on the
        client side.  If success, cached list of sensor readings, i.e.
        self.sensor.readings, is reset back to empty (to reduce
        possibility of overloading server memory).
        """
        # Receive all data from new client and decode
        self.request = self.my_recv_all()
        self.decode_request()

        # Process based on information requested by client.
        # Info is either environmental parameters or audio data.
        if self.client_request == "env_params":
            self.client_socket.sendall(self.send_sensors())

            # Client will respond to whether or not the write
            # to the InfluxDB was successful
            self.request = self.my_recv_all()
            self.decode_request()

            # self.client_request is now either "success" or "not success"
            print("Write to influx: {}".format(self.client_request))
            if self.client_request == "success":
                
                # clear sensor cache
                self.sensors.readings = []

                # respond that cache has been cleared.
                self.client_socket.sendall("Received: {}. self.readings = {}".format(self.client_request,
                                                                                     self.sensors.readings).encode())
            elif self.client_request == "not success":
                # Respond that cache has not been cleared
                self.client_socket.sendall("self.readings has not been cleared".encode())
            print("self.readings: {}".format(self.sensors.readings))

            # Close socket
            self.client_socket.close()
            
        elif self.client_request == "audio":
            print("audio")
        
        # Make sure socket is closed
        self.client_socket.close()




if __name__=='__main__':
    """
    Upon initialization of the program, the configuration file is read
    in and passed to the Server.  The Server is responsible for gathering
    and caching sensor data until a request is received from a client.
    Depending on the data requested, the Server will either send audio
    data or environmental parameters.
    """
    settings = import_server_conf()
    try:
        s = Server(settings)
    except Exception as e:
        logging.CRITICAL(e)
    
