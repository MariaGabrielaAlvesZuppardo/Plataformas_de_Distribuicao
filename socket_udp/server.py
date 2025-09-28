import socket
import json
import time

HOST = "0.0.0.0"
PORT = 5005

clientes = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Servidor UDP escutando em {HOST}:{PORT}...\n")

while True:
    data, addr = sock.recvfrom(8192)
    try:
        mensagem = json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Erro ao decodificar JSON de {addr}: {e}")
        continue

    clientes[addr[0]] = {
        "ultima_metrica": mensagem,
        "ultimo_tempo": time.strftime("%H:%M:%S")
    }

    print("\n=== Clientes Conectados ===")
    for ip, info in clientes.items():
        print(f"\n{ip} @ {info['ultimo_tempo']}")
        met = info["ultima_metrica"]

        # CPU
        print(f"CPU: média {met['cpu']['media']}% | por núcleo {met['cpu']['por_nucleo']}")

        # Memória
        mem = met['memoria']
        print(f"Memória: total {mem['total_MB']}MB | usada {mem['usada_MB']}MB | livre {mem['livre_MB']}MB")

        # Disco
        disk = met['disco']
        print(f"Disco: total {disk['uso_total_GB']}GB | usado {disk['usado_GB']}GB | livre {disk['livre_GB']}GB | "
              f"leitura {disk['taxa_leitura_MBps']}MB/s | escrita {disk['taxa_escrita_MBps']}MB/s")

        # Rede
        net = met['rede']
        print(f"Rede: upload {net['taxa_upload_MBps']}MB/s | download {net['taxa_download_MBps']}MB/s | "
              f"pacotes perdidos {net['pacotes_perdidos']}")
