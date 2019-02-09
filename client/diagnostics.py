import numpy as np
import socket



def monitor(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            try:
                data=False
                s.connect((HOST, PORT))
                data = s.recv(1024)
                if not data==False:
                    print('Received', repr(data))
                    s.sendall(b'Hi')
                    return data
            except:
                print("Antsle is not ready to send new data")

if __name__ == '__main__':
    HOST = '192.168.0.201'  # The server's hostname or IP address
    PORT = 65432        # The port used by the server
    dat={}
    dat=monitor(HOST,PORT)
    print("Received ",dat)

