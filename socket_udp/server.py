import socket 
import json 
import time 

# Configurações do Servidor : 

HOST = "0.0.0.0" # Executa em todas as interfaces 

PORT = 5005 # Porta do Servidor 

# Estrutura em memória: { ip_cliente: { "ultima_metrica": {...}, "ultimo_tempo": ... } }

clientes = {}

#Criando o socket UDP 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST,PORT))

print(f"Sevidor UDP executando em {HOST}:{PORT}...")

while True:
    data,addr = sock.recvfrom(4096) #Recebe Pacotes 
    try:
        mensagem = json.loads(data.decode("utf-8"))
    except:
        continue

    #Atualiza os dados do cliente 

    clientes[addr[0]] = {
        "ultima_metrica":mensagem,
        "ultimo_tempo": time.strftime("%H:%M:%S")
    }

    # Exibindo estado atual 

    print("\n=== Clientes Conectados ===")

    for ip, info in clientes.items():
        print(f"{ip} @{info['ultimo_tempo']}-> {info['ultima_metrica']}")