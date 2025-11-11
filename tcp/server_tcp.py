import socket
import threading

HOST = '0.0.0.0'
PORT = 5000 

clients = []
nicknames = {}

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                raise Exception("Cliente desconectado")

            msg_decoded = message.decode('utf-8')
            
            if msg_decoded.startswith('/nick '):
                nickname = msg_decoded.split(' ', 1)[1]
                nicknames[client_socket] = nickname
                client_socket.send(f"Seu nome agora é {nickname}".encode('utf-8'))
                broadcast(f"{nickname} entrou no chat!".encode('utf-8'), client_socket)
                
            elif msg_decoded.startswith('/sair'):
                raise Exception("Comando /sair executado")
                
            elif msg_decoded.startswith('/bench '):
                broadcast(message, client_socket)
            
            else:
                if client_socket in nicknames:
                    sender = nicknames[client_socket]
                    full_message = f"{sender}: {msg_decoded}"
                    print(f"Mensagem de {sender}: {msg_decoded}")
                    broadcast(full_message.encode('utf-8'), client_socket)
                else:
                    client_socket.send("Defina um /nick primeiro.".encode('utf-8'))

        except:
            if client_socket in clients:
                clients.remove(client_socket)
                
            if client_socket in nicknames:
                nickname = nicknames.pop(client_socket)
                print(f"Desconexão de {nickname}")
                broadcast(f"{nickname} saiu do chat.".encode('utf-8'))
                
            client_socket.close()
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Servidor TCP rodando em {HOST}:{PORT}")
    while True:
        client_socket, address = server.accept()
        print(f"Nova conexão de {str(address)}")

        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    main()