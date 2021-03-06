import socket

def main():

    server = "192.168.20.12"
    host =  "192.168.20.9"
    server = socket.gethostbyname(server)

    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.bind((host, 9999))

    client_socket.connect((server, 8821))

    data = client_socket.recv(1024)
    print("received:", data)

    message = ''
    while message != 'EXIT':
        message = input("Insert E to exit, D to delete, or the name of a file in this directory for the query.\n")
        if message == "E" or message == "D":
            client_socket.sendto(message.encode(), (server, 8821))
        else:
            file = open(message, "rb")
            SendData = file.read(1024)
            client_socket.send(SendData)
        data = client_socket.recv(1024)
        print("received:", data)

if __name__ == "__main__":
    main()
