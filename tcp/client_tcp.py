import socket
import threading

HOST = "127.0.0.1"
PORT = 5001
NICKNAME = "Default"
SERVER_ADDR = (HOST, PORT)


def receive(client_socket):
    pass


def write(client_socket):
    pass


def bench_test(client_socket, size_bytes):
    pass


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(0.5)

    # Cliente UDP se conecta enviando o /nick para o servidor [cite: 34]
    client.sendto(f"/nick {NICKNAME}".encode("utf-8"), SERVER_ADDR)

    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write, args=(client,))
    write_thread.start()


if __name__ == "__main__":
    main()
