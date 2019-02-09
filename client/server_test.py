import socket

def main():
    while (True):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('localhost', 8089))
        clientsocket.send('vala')
if __name__ == '__main__':
    main()

