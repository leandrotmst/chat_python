import socket
import threading
import sys
import time # Necessário para o /bench

# Configurações - Seu IP Corrigido deve estar aqui
HOST = '192.168.0.131'
PORT = 5000

NICKNAME = "Anônimo"

def receive_messages(client_socket):
    """Thread dedicada a receber mensagens do servidor."""
    global NICKNAME
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            
            if not message:
                print("\nServidor desconectado. Encerrando...")
                client_socket.close()
                sys.exit()
                
            if message.startswith("Seu nome agora é"):
                try:
                    novo_nome = message.split("'")[1] 
                    NICKNAME = novo_nome
                except:
                    pass
            
            # IMPRESSÃO OTIMIZADA: Garante que o prompt anterior seja quebrado antes de imprimir a mensagem
            print(f"\n{message}")
            sys.stdout.write(f"Você ({NICKNAME}): ")
            sys.stdout.flush()

        except:
            break

def main():
    global NICKNAME
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print(f"✅ Conectado ao Servidor TCP em {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"❌ Não foi possível conectar ao servidor em {HOST}:{PORT}.")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    print("Digite mensagens ou comandos (ex: /nick MeuNome, /sair, /bench <bytes>)")
    while True:
        try:
            user_input = input(f"Você ({NICKNAME}): ")

            if user_input.startswith('/'):
                partes = user_input.split()
                comando = partes[0]
                
                if comando == '/sair':
                    client.send("/sair".encode('utf-8'))
                    client.close()
                    break

                elif comando == '/nick':
                    if len(partes) > 1:
                        client.send(user_input.encode('utf-8'))
                    else:
                        print("Uso: /nick <seu_nome>")

                elif comando == '/bench':
                    if len(partes)!=2:
                        print("Uso: /bench <bytes>")
                        continue
                    try:
                        bytes_to_send = int(partes[1])
                    except ValueError:
                        print("O argumento <bytes> deve ser um número inteiro.")
                        continue

                    print(f"Iniciando benchmark TCP. Enviando {bytes_to_send} bytes...")

                    data = b'A' * bytes_to_send 
                    start_time = time.time()
                    
                    total_sent = 0
                    while total_sent < bytes_to_send:
                        sent = client.send(data[total_sent:])
                        if sent == 0:
                            raise RuntimeError("Socket connection broken")
                        total_sent += sent
                    
                    elapsed_time = time.time() - start_time
                    speed_mbps = (bytes_to_send / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0
                    
                    print("-" * 30)
                    print("✅ Benchmark TCP concluído.")
                    print(f"Tempo total: {elapsed_time:.4f} segundos")
                    print(f"Velocidade média: {speed_mbps:.2f} MB/s")
                    print("-" * 30)
                
                else:
                    print(f"Comando desconhecido: {comando}")
            
            else:
                if user_input.strip():
                    client.send(user_input.encode('utf-8'))

        except:
            break

if __name__ == "__main__":
    main()