import my_photo
import json
import socket
import sys
from datetime import datetime

def import_conf(config_file, server_id):
    with open(config_file, 'r') as f:
        ip_line = [line.strip('\n') for line in f if server_id in line]
        assert len(ip_line) == 1
        return ip_line[0].split(" ")[1]
        # print(ip_line)

def create_message(params = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "temp", "rh"]):
    # dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params = '\r\n'.join(params)
    print(params)

def get_data(server_ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    test_file = "/Users/corymosiman/Dropbox/ARPA-E SENSOR Project Folder/3 Tasks/1 HPDmobile/Documents/secondPurchaseDiagram.pdf"
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
    server_id = sys.argv[1]
    server_ip = import_conf('client.conf', server_id)
    print(server_ip)
    create_message()
    # get_data(server_ip)
