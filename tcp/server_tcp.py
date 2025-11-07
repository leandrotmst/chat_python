import socket 

HOST='0.0.0.0'
PORT=9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(5)

while True:
    client, addr = server.accept()
    print(client.recv(1024).decode())
    client.send('Seja bem-vindo'.encode('utf-8'))
    