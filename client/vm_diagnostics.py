#this runs in SERVER (locally on the laptop)
import socket

def main():
    while True:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('192.168.0.206', 8089))
        serversocket.listen(5) # become a server socket, maximum 5 connections
        connection, address = serversocket.accept()
        #buf = connection.recv(64)
        #if len(buf) > 0:
            #print(buf)
        str = "hi"
        b = str.encode()
        serversocket.send(b)
if __name__ == '__main__':
    main()
        
