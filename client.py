import socket
import psutil
import time 

def coletar_metricas_cpu():
    #Coletando métricas do uso do CPU por núcleo e por média
    uso_por_nucleo = psutil.cpu_percent(percpu=True)
    media = psutil.cpu_percent()
    return {
        "por_nucleo" : uso_por_nucleo,
        "media": media
    }

def start_client(server_host="127.0.0.1", server_port=5000, intervalo=5):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))
    print(f"[CLIENTE] Conectado ao servidor {server_host}:{server_port}")

    try:
        while True:
            metricas = coletar_metricas_cpu()
            mensagem = f"CPU -> Núcleos: {metricas['por_nucleo']} | Média: {metricas['media']}%"
            client.send(mensagem.encode())
            time.sleep(intervalo)  # envia periodicamente
    except KeyboardInterrupt:
        print("[CLIENTE] Encerrado manualmente.")
    finally:
        client.close()


if __name__ == "__main__":
    start_client()