import socket
import threading

HOST = "0.0.0.0"
PORT = 5000  # Porta também usada pelo ESP32 [cite: 51]


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    clients = []
    nicknames = {}

    def broadcast(message, sender_socket):
        pass

    def handle_client(client_socket):
        pass

    print(f"Servidor TCP rodando em {HOST}:{PORT}")
    while True:
        client_socket, address = server.accept()
        print(f"Nova conexão de {str(address)}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == "__main__":
    main()
