import socket

HOST = "0.0.0.0"
PORT = 5001


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    clients_addrs = {}  # {addr: nickname}

    print(f"Servidor UDP rodando em {HOST}:{PORT}")
    while True:
        data, addr = server.recvfrom(1024)
        message = data.decode("utf-8")

        # Implementar lógica de /nick <nome> [cite: 34]
        # Implementar retransmissão manual para todos os clientes [cite: 33]
        pass


if __name__ == "__main__":
    main()
