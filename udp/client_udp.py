import socket
import threading
import sys
import time # Necessário para o /bench

# Configurações - Seu IP Corrigido deve estar aqui
HOST = '192.168.0.131' 
PORT = 5001

client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NICKNAME = "Anônimo"

def receive_messages_udp():
    """Thread dedicada a receber datagramas do servidor."""
    while True:
        try:
            message, server_addr = client_udp.recvfrom(1024) 
            message_str = message.decode('utf-8')
            
            if not message:
                continue 
            
            if message_str.startswith("Seu nome agora é"):
                global NICKNAME
                try:
                    novo_nome = message_str.split("'")[1] 
                    NICKNAME = novo_nome
                except:
                    pass
            
            # IMPRESSÃO OTIMIZADA: Garante nova linha e reimprime o prompt
            print(f"\n{message_str}")
            sys.stdout.write(f"Você ({NICKNAME}): ")
            sys.stdout.flush()

        except Exception:
            break

def main():
    global NICKNAME
    
    # Envia uma mensagem inicial para registrar o endereço no servidor
    client_udp.sendto(f"/nick {NICKNAME}".encode('utf-8'), (HOST, PORT))
    print(f"✅ Inicializado e registrado no Servidor UDP em {HOST}:{PORT}")

    receive_thread = threading.Thread(target=receive_messages_udp)
    receive_thread.daemon = True
    receive_thread.start()

    print("Digite mensagens ou comandos (ex: /nick MeuNome, /sair, /bench <bytes>)")
    while True:
        try:
            user_input = input(f"Você ({NICKNAME}): ")
            
            if user_input.startswith('/'):
                partes = user_input.split()
                comando = partes[0]
                
                if comando == '/sair': # encerra a conexão [cite: 42]
                    client_udp.sendto("/sair".encode('utf-8'), (HOST, PORT))
                    client_udp.close()
                    break

                elif comando == '/nick': # define o nome do cliente [cite: 41]
                    if len(partes) > 1:
                         client_udp.sendto(user_input.encode('utf-8'), (HOST, PORT))
                    else:
                         print("Uso: /nick <seu_nome>")

                elif comando == '/bench':
                    if len(partes) != 2:
                        print("Uso: /bench <bytes>")
                        continue
                    try:
                        bytes_to_send = int(partes[1])
                    except ValueError:
                        print("O argumento <bytes> deve ser um número inteiro.")
                        continue
                        
                    MAX_DATAGRAM_SIZE = 1400 
                    print(f"Iniciando benchmark UDP. Enviando {bytes_to_send} bytes...")

                    data = b'A' * bytes_to_send 
                    start_time = time.time()
                    
                    total_sent = 0
                    while total_sent < bytes_to_send:
                        chunk = data[total_sent:total_sent + MAX_DATAGRAM_SIZE]
                        client_udp.sendto(chunk, (HOST, PORT))
                        total_sent += len(chunk)

                    elapsed_time = time.time() - start_time
                    speed_mbps = (bytes_to_send / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0

                    print("-" * 30)
                    print("✅ Benchmark UDP concluído.")
                    print(f"Tempo total: {elapsed_time:.4f} segundos")
                    print(f"Velocidade média: {speed_mbps:.2f} MB/s")
                    print("-" * 30)

                else:
                    print(f"Comando desconhecido: {comando}")
            
            else:
                if user_input.strip():
                    client_udp.sendto(user_input.encode('utf-8'), (HOST, PORT))

        except:
            break

if __name__ == "__main__":
    main()