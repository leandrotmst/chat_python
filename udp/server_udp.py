import socket

HOST = '0.0.0.0'
PORT = 5001

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    clients_addrs = {} 

    print(f"Servidor UDP rodando em {HOST}:{PORT}")
    while True:
        try:
            data, addr = server.recvfrom(65535) # Tamanho máximo do datagrama
            message = data.decode('utf-8')

            if message.startswith('/nick '):
                nickname = message.split(' ', 1)[1]
                old_nickname = clients_addrs.get(addr, 'Novo Cliente')
                clients_addrs[addr] = nickname
                print(f"Registro: {old_nickname} -> {nickname} em {addr}")
                
            elif message == '/sair':
                if addr in clients_addrs:
                    nickname = clients_addrs.pop(addr)
                    print(f"Desconexão de {nickname} em {addr}")
                    broadcast_msg = f"{nickname} saiu do chat UDP.".encode('utf-8')
                    for client_addr in clients_addrs:
                        server.sendto(broadcast_msg, client_addr)
                        
            elif message.startswith('/bench-data:'):
                sender_nick = clients_addrs.get(addr, 'Desconhecido')
                print(f"Recebido pacote de bench de {sender_nick} ({len(data)} bytes)")
                
            else:
                sender_nick = clients_addrs.get(addr, 'Desconhecido')
                full_message = f"[{sender_nick}]: {message}"
                print(f"Mensagem recebida de {sender_nick} ({addr}): {message}")
                
                for client_addr in clients_addrs:
                    if client_addr != addr:
                        server.sendto(full_message.encode('utf-8'), client_addr)
                        
        except Exception as e:
            print(f"Erro no processamento UDP: {e}")