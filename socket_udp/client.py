import socket
import json
import psutil
import time

# Se cliente e servidor estão na mesma máquina:
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5005
INTERVAL = 5  # segundos

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Guardar valores anteriores para calcular taxas
prev_disk = psutil.disk_io_counters()
prev_net = psutil.net_io_counters()
time.sleep(1)  # garantir referência inicial

while True:
    # ===== CPU =====
    cpu_por_nucleo = psutil.cpu_percent(interval=1, percpu=True)
    cpu_media = psutil.cpu_percent(interval=None)

    # ===== Memória =====
    mem = psutil.virtual_memory()
    memoria = {
        "total_MB": round(mem.total / (1024 * 1024), 2),
        "usada_MB": round(mem.used / (1024 * 1024), 2),
        "livre_MB": round(mem.available / (1024 * 1024), 2)
    }

    # ===== Disco =====
    disco = psutil.disk_usage('/')
    disco_io = psutil.disk_io_counters()
    tempo = INTERVAL
    taxa_leitura = (disco_io.read_bytes - prev_disk.read_bytes) / tempo / (1024 * 1024)
    taxa_escrita = (disco_io.write_bytes - prev_disk.write_bytes) / tempo / (1024 * 1024)
    prev_disk = disco_io

    disco_metrica = {
        "uso_total_GB": round(disco.total / (1024 * 1024 * 1024), 2),
        "usado_GB": round(disco.used / (1024 * 1024 * 1024), 2),
        "livre_GB": round(disco.free / (1024 * 1024 * 1024), 2),
        "taxa_leitura_MBps": round(taxa_leitura, 2),
        "taxa_escrita_MBps": round(taxa_escrita, 2),
    }

    # ===== Rede =====
    net = psutil.net_io_counters()
    taxa_upload = (net.bytes_sent - prev_net.bytes_sent) / tempo / (1024 * 1024)
    taxa_download = (net.bytes_recv - prev_net.bytes_recv) / tempo / (1024 * 1024)
    pacotes_perdidos = (net.dropin - prev_net.dropin) + (net.dropout - prev_net.dropout)
    prev_net = net

    rede = {
        "taxa_upload_MBps": round(taxa_upload, 2),
        "taxa_download_MBps": round(taxa_download, 2),
        "pacotes_perdidos": pacotes_perdidos
    }

    # ===== Consolida =====
    dados = {
        "cpu": {"por_nucleo": cpu_por_nucleo, "media": cpu_media},
        "memoria": memoria,
        "disco": disco_metrica,
        "rede": rede
    }

    mensagem = json.dumps(dados).encode("utf-8")
    sock.sendto(mensagem, (SERVER_HOST, SERVER_PORT))

    print(f"[Cliente] Dados enviados: {dados}")
    time.sleep(INTERVAL)
