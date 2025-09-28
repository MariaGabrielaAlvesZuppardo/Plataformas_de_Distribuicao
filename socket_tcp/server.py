import socket 
import threading

#Armazenando dados em memória {enderco_cliente: [metricas_recebidas]}

dados_clientes = {}

def handle_client(conn,addr):
    print(f"[NOVA CONEXÃO] Cliente {addr} conectado.")
    dados_clientes[addr] = [] #Incializa a lista de métricas desse cliente 

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break # O cliente descontectou 
            mensagem = data.decode()
            print(f"[DADOS RECEBIDOS de {addr}]{mensagem}")

            #Armazena em memória 
            dados_clientes[addr].append(mensagem)
    
    except:
        pass
    finally:
        print(f"[DESCONECTADO]Cliente {addr}")
        conn.close()
        del dados_clientes[addr]
    
def start_server(host="0.0.0.0",port = 5000):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host,port))
    server.listen()

    print(f"[SERVIDOR] Rodando em {host}:{port}")

    while True:
        conn,addr = server.accept()
        thread = threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()

        #Exibe quais são os clientes conectados 
        print(f"[STATUS] Clientes conectados: {len(dados_clientes)}")

if __name__ == "__main__":
    start_server()