import socket
import threading
import sys
import time
import os

HOST = '192.168.0.198' # Seu IP
PORT = 5000
NICKNAME = 'ClienteTCP'

def receive(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[SERVIDOR DESCONECTADO]")
                client_socket.close()
                os._exit(0)
            
            if not message.startswith(f"{NICKNAME}:"):
                print(message)
                
        except ConnectionResetError:
            print("\n[ERRO: Conexão perdida com o servidor]")
            client_socket.close()
            os._exit(0)
        except:
            client_socket.close()
            os._exit(0)

def bench_test(client_socket, size_bytes):
    try:
        data_size = int(size_bytes)
        data = b'A' * data_size
        
        start_time = time.time()
        client_socket.sendall(data)
        end_time = time.time()
        
        total_time = end_time - start_time
        data_mb = data_size / (1024 * 1024)
        
        print(f"\n--- TESTE DE DESEMPENHO TCP CONCLUÍDO ---")
        print(f"Volume de dados: {data_mb:.2f} MB")
        print(f"Tempo total de envio: {total_time:.4f} segundos")
        print("------------------------------------------")

    except ValueError:
        print("Uso correto: /bench <bytes>")
    except Exception as e:
        print(f"Erro no teste de benchmark: {e}")

def write(client_socket):
    global NICKNAME
    
    client_socket.send(f"/nick {NICKNAME}".encode('utf-8'))
    
    while True:
        try:
            user_input = sys.stdin.readline().strip()
            
            if user_input.startswith('/nick '):
                _, new_nick = user_input.split(' ', 1)
                NICKNAME = new_nick
                client_socket.send(user_input.encode('utf-8'))
                
            elif user_input == '/sair':
                client_socket.send(user_input.encode('utf-8'))
                client_socket.close()
                print("[DESCONEXÃO INICIADA]")
                os._exit(0)
                
            elif user_input.startswith('/bench '):
                _, size_bytes = user_input.split(' ', 1)
                bench_test(client_socket, size_bytes)
                
            elif user_input.startswith('led_on') or user_input.startswith('led_off'):
                 client_socket.send(user_input.encode('utf-8'))
                 
            else:
                message = f"{user_input}"
                client_socket.send(message.encode('utf-8'))
                
        except:
            break

def main():
    print(f"Iniciando Cliente TCP. Nick inicial: {NICKNAME}")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"ERRO: Conexão recusada. Verifique se o servidor {HOST}:{PORT} está rodando.")
        return

    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write, args=(client,))
    write_thread.start()

if __name__ == '__main__':
    main()