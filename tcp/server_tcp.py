import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

clientes = []
esp32_socket = None

def broadcast(message, remetente_socket):
    """Retransmite a mensagem para todos os clientes, exceto o remetente."""
    for client_socket, nome in clientes:
        if client_socket != remetente_socket:
            try:
                client_socket.send(message)
            except:
                remove_cliente(client_socket)

def remove_cliente(client_socket):
    """Remove um cliente da lista e fecha sua conexão."""
    global esp32_socket
    if client_socket == esp32_socket:
        esp32_socket = None
        print("Atenção: ESP32 desconectado.")
        
    for i, (sock, nome) in enumerate(clientes):
        if sock == client_socket:
            print(f"Desconectando cliente '{nome}' de {sock.getpeername()}")
            clientes.pop(i)
            sock.close()
            broadcast(f"Servidor: {nome} saiu do chat.".encode('utf-8'), client_socket)
            break

def process_message(full_message, client_socket):
    """Analisa a mensagem recebida e executa comandos ou faz o broadcast."""
    global esp32_socket 
    
    nome_remetente = "Anônimo"
    for i, (sock, nome) in enumerate(clientes):
        if sock == client_socket:
            nome_remetente = nome
            break

    # 1. COMANDOS DE CHAT/BENCHMARK
    if full_message.startswith('/'):
        partes = full_message.split()
        comando = partes[0]
        
        if comando == '/nick': # define o nome do cliente [cite: 41]
            if len(partes) > 1:
                novo_nome = partes[1]
                for i, (sock, nome) in enumerate(clientes):
                    if sock == client_socket:
                        clientes[i] = (sock, novo_nome)
                        print(f"-> '{nome}' mudou o nome para '{novo_nome}'")
                        client_socket.send(f"Seu nome agora é '{novo_nome}'.".encode('utf-8'))
                        broadcast(f"Servidor: {nome_remetente} agora é {novo_nome}.".encode('utf-8'), client_socket)
                        break
            else:
                client_socket.send("Uso: /nick <seu_nome>".encode('utf-8'))

        elif comando == '/sair': # encerra a conexão [cite: 42]
            client_socket.close() 
            
        elif comando == '/bench': # Benchmark [cite: 59]
            print(f"Cliente {nome_remetente} iniciou um Benchmark TCP. Recebendo dados...")

        else:
            client_socket.send(f"Comando desconhecido: {comando}".encode('utf-8'))

    # 2. COMANDOS DIRECIONADOS AO ESP32 (led_on/led_off)
    elif full_message.lower().strip() in ["led_on", "led_off"]:
        if esp32_socket:
            try:
                esp32_socket.send(full_message.encode('utf-8'))
                client_socket.send(f"Comando '{full_message.strip().upper()}' enviado para o ESP32.".encode('utf-8'))
                print(f"Comando '{full_message.strip().upper()}' enviado ao ESP32 por {nome_remetente}.")
            except:
                client_socket.send("Erro: Não foi possível enviar comando ao ESP32.".encode('utf-8'))
        else:
            client_socket.send("Erro: ESP32 não está conectado.".encode('utf-8'))

    # 3. MENSAGENS DO ESP32 (Dados ou Confirmação)
    elif "esp32" in full_message.lower() and ("data" in full_message.lower() or "led aceso" in full_message.lower() or "led apagado" in full_message.lower()):
        print(f"Recebido do ESP32: {full_message}")
        
        if nome_remetente == "Anônimo":
            for i, (sock, nome) in enumerate(clientes):
                if sock == client_socket:
                    clientes[i] = (sock, "ESP32")
                    esp32_socket = sock
                    print("Socket do ESP32 identificado e armazenado.")
                    break
        
        broadcast(f"[ESP32]: {full_message}".encode('utf-8'), client_socket)
        
    # 4. MENSAGEM NORMAL (Broadcast)
    else:
        formatted_message = f"[{nome_remetente}]: {full_message}".encode('utf-8')
        print(f"Recebido de {nome_remetente} ({client_socket.getpeername()}): {full_message}")
        broadcast(formatted_message, client_socket)


def handle_client(client_socket, addr):
    """Executado em uma thread para cada cliente."""
    print(f"✅ Novo cliente conectado: {addr}")
    clientes.append((client_socket, "Anônimo")) 

    try:
        while True:
            message = client_socket.recv(1024) 
            if not message:
                break
            process_message(message.decode('utf-8'), client_socket)
    except:
        pass
    
    remove_cliente(client_socket)
    print(f"❌ Cliente desconectado: {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor TCP escutando em {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.close()

if __name__ == "__main__":
    main()