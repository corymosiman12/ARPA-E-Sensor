import socket
import threading
import os
import sys
import logging
from datetime import datetime
import re

# Set logging level and format logging entries.
logging.basicConfig(filename = 'server_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

def import_server_conf(config_file):
    try:
        with open(config_file, 'r') as f:
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
        self.settings = settings
        self.host = ''
        self.port = int(self.settings['listen_port'])
        self.root = self.settings['root']
        self.create_socket()


    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print("Listen socket created on port: {}".format(self.port))
        self.sock = sock
        while True:
            (client_socket, client_address) = self.sock.accept()
            if client_socket:
                thr = Multiple(client_socket, client_address, self.settings)
                thr.start()
                print("New connection with: {}".format(client_address))

class Multiple(threading.Thread):
    def __init__(self, socket, address, settings):
        threading.Thread.__init__(self)
        self.client_socket = socket
        self.client_address = address
        self.size = 4096
        self.settings = settings
    
    def read_params(self, params)
        vals = []
        for p in params:
            vals.append(p + "_" + str(self.my_read))
        return " ".join(vals)

    def my_read_adc(self, param):

    def decode_request(self, request):
        decoded = request.decode().split('\r\n')
        client_request_time = decoded[0]
        params = decoded[1:]
        return (client_request_time, params)

    def run(self):
        request = b''
        partial_request = self.client_socket.recv(self.size)
        while len(partial_request) == self.size:
            # print(len(partial_request))
            request += partial_request
            partial_request = self.client_socket.recv(self.size)
        if len(partial_request) < self.size and len(partial_request) != 0:
            request += partial_request
        client_request_time, params = self.decode_request(request)
        self.client_socket.close()




if __name__=='__main__':
    # Upon initialization of the program, the ws.conf file is read in using the import_ws_conf function.  This
    # function is defined outside of a class so that the settingsDict and settingsKeys variables will be available
    # to the 'Threading' class as well.
    settings = import_server_conf('server.conf')
    print(settings)
    try:
        s = Server(settings)
    except Exception as e:
        logging.CRITICAL(e)
    