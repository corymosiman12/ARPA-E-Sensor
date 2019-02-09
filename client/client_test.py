import numpy as np
import socket

def send():
    get_sensors_response=[1,2,3,4]
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
        ss.bind((HOST, PORT))
        ss.listen(5)
        conn, addr = ss.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024) #Just send a Hi from the remote computer to inform that he has received the data
                if data:
                    break
                conn.sendall(get_sensors_response)
if __name__ == '__main__':
    send()
