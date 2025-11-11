import socket
import threading
import sys
import time
import os

HOST = '192.168.0.198'
PORT = 5001
NICKNAME = 'ClienteUDP'
SERVER_ADDR = (HOST, PORT)

def receive(client_socket):
    while True:
        try:
            data, addr = client_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(message)
            
        except socket.timeout:
            pass
        except:
            client_socket.close()
            os._exit(0)

def bench_test(client_socket, size_bytes):
    try:
        data_size = int(size_bytes)
        
        if data_size > 60000:
             print("Aviso: O UDP pode limitar o tamanho do pacote (Max ~60KB por datagrama).")
             
        data = b'A' * data_size
        
        start_time = time.time()
        
        client_socket.sendto(f"/bench-data:{data_size}".encode('utf-8'), SERVER_ADDR) 
        client_socket.sendto(data, SERVER_ADDR)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        data_mb = data_size / (1024 * 1024)
        
        print(f"\n--- TESTE DE DESEMPENHO UDP CONCLUÍDO ---")
        print(f"Volume de dados: {data_mb:.2f} MB")
        print(f"Tempo total de envio: {total_time:.4f} segundos")
        print("------------------------------------------")

    except ValueError:
        print("Uso correto: /bench <bytes>")
    except Exception as e:
        print(f"Erro no teste de benchmark: {e}")


def write(client_socket):
    global NICKNAME
    
    client_socket.sendto(f"/nick {NICKNAME}".encode('utf-8'), SERVER_ADDR)
    
    while True:
        try:
            user_input = sys.stdin.readline().strip()
            
            if user_input.startswith('/nick '):
                _, new_nick = user_input.split(' ', 1)
                NICKNAME = new_nick
                client_socket.sendto(user_input.encode('utf-8'), SERVER_ADDR)
                
            elif user_input == '/sair':
                client_socket.sendto(user_input.encode('utf-8'), SERVER_ADDR)
                client_socket.close()
                print("[DESCONEXÃO INICIADA]")
                os._exit(0)
                
            elif user_input.startswith('/bench '):
                _, size_bytes = user_input.split(' ', 1)
                bench_test(client_socket, size_bytes)
                
            else:
                client_socket.sendto(user_input.encode('utf-8'), SERVER_ADDR)
                
        except:
            break

def main():
    print(f"Iniciando Cliente UDP. Nick inicial: {NICKNAME}")
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(0.1)
    
    
    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write, args=(client,))
    write_thread.start()

if __name__ == '__main__':
    main()