import socket
import threading

# Configurações UDP
HOST = '0.0.0.0'
PORT = 5001 # Usar uma porta diferente do TCP (5000) para evitar conflitos

# Dicionário para armazenar os clientes: {addr: nome}
# addr é uma tupla (ip, porta)
clientes_udp = {}

# Criação do socket UDP
server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_udp.bind((HOST, PORT))
print(f"Servidor UDP escutando em {HOST}:{PORT}")
print("Aguardando mensagens...")

def broadcast_udp(message, remetente_addr):
    """Envia a mensagem para todos os clientes, exceto o remetente."""
    for addr, nome in clientes_udp.items():
        if addr != remetente_addr:
            try:
                server_udp.sendto(message, addr)
            except Exception as e:
                print(f"Erro ao enviar para {addr}: {e}")

def process_message_udp(full_message, addr):
    """Analisa a mensagem recebida e executa comandos ou faz o broadcast."""
    
    # Decodifica a mensagem (Tenta decodificar, mas pode falha se for dado binário)
    try:
        message_str = full_message.decode('utf-8')
    except UnicodeDecodeError:
        # Se não for uma string UTF-8 válida (pacote de dado do benchmark)
        if addr in clientes_udp:
             print(f"Recebendo pacote de dados brutos do benchmark de {clientes_udp[addr]} ({addr})...")
        else:
             print(f"Recebendo pacote de dados brutos de cliente desconhecido ({addr})...")
        return # Sai da função, não faz broadcast

    # Tenta obter o nome do remetente, ou usa "Anônimo"
    nome_remetente = clientes_udp.get(addr, "Anônimo")
    
    # 1. Verifica se é um comando
    if message_str.startswith('/'):
        partes = message_str.split()
        comando = partes[0]

        if comando == '/nick': # Comando /nick <nome> [cite: 34]
            if len(partes) > 1:
                novo_nome = partes[1]
                if addr in clientes_udp:
                    print(f"-> '{nome_remetente}' ({addr}) mudou o nome para '{novo_nome}'")
                
                # Adiciona/Atualiza o cliente e seu nome
                clientes_udp[addr] = novo_nome
                
                server_udp.sendto(f"Seu nome agora é '{novo_nome}'.".encode('utf-8'), addr)
                
                # Avisa os outros
                broadcast_udp(f"Servidor: {nome_remetente} agora é {novo_nome}.".encode('utf-8'), addr)
                
            else:
                server_udp.sendto("Uso: /nick <seu_nome>".encode('utf-8'), addr)

        elif comando == '/sair': # Comando /sair [cite: 42]
            # UDP é sem conexão, mas removemos o endereço para parar o broadcast
            if addr in clientes_udp:
                print(f"❌ Cliente '{nome_remetente}' saiu (UDP): {addr}")
                del clientes_udp[addr]
                broadcast_udp(f"Servidor: {nome_remetente} saiu do chat.".encode('utf-8'), addr)

        elif comando == '/bench': # Comando /bench <bytes> [cite: 59]
             print(f"Comando /bench UDP recebido de {nome_remetente} em {addr}. Início do tráfego de benchmark.")
             # O servidor não faz nada além de registrar.

        else:
            server_udp.sendto(f"Comando desconhecido: {comando}".encode('utf-8'), addr)
            
    # 2. Se não for comando, é uma mensagem normal para broadcast
    else:
        # Garante que o cliente esteja cadastrado antes de fazer o broadcast
        if addr not in clientes_udp:
             clientes_udp[addr] = "Anônimo"
        
        formatted_message = f"[{nome_remetente}]: {message_str}".encode('utf-8')
        print(f"Recebido de {nome_remetente} ({addr}): {message_str}")
        broadcast_udp(formatted_message, addr)


def receive_loop_udp():
    """Loop principal para receber todos os datagramas."""
    try:
        while True:
            # Recebe o datagrama e o endereço do remetente
            data, addr = server_udp.recvfrom(1024)
            
            # O processamento é delegado a uma função para manter o loop rápido
            process_message_udp(data, addr)
            
    except KeyboardInterrupt:
        print("\nServidor UDP encerrado pelo usuário.")
    except Exception as e:
        print(f"\nOcorreu um erro no loop UDP: {e}")
    finally:
        server_udp.close()

if __name__ == "__main__":
    receive_loop_udp()