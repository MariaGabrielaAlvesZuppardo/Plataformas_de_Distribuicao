import asyncio
import time
import psutil
import uuid
import httpx
import argparse


class MonitoringAgent:
    def __init__(self, client_id=None, interval=5, server_url="http://127.0.0.1:8000/ingest"):
        self.client_id = client_id or str(uuid.uuid4())
        self.interval = interval
        self.server_url = server_url

        # previous state para taxas
        self.prev_disk = psutil.disk_io_counters()
        self.prev_net = psutil.net_io_counters()
        self.prev_time = time.time()

    def collect_metrics(self):
        now = time.time()
        cpu_per_core = psutil.cpu_percent(percpu=True)
        cpu_avg = psutil.cpu_percent(percpu=False)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        current_disk_io = psutil.disk_io_counters()
        current_net_io = psutil.net_io_counters()

        elapsed = max(now - self.prev_time, 1.0)

        metrics = {
            "cpu": {"per_core": cpu_per_core, "avg": cpu_avg},
            "memory": {
                "total": vm.total, "used": vm.used,
                "free": vm.available, "percent": vm.percent
            },
            "disk": {
                "total": disk.total, "used": disk.used,
                "free": disk.free, "percent": disk.percent,
                "read_bytes_per_s": (current_disk_io.read_bytes - self.prev_disk.read_bytes) / elapsed,
                "write_bytes_per_s": (current_disk_io.write_bytes - self.prev_disk.write_bytes) / elapsed,
            },
            "net": {
                "bytes_sent_per_s": (current_net_io.bytes_sent - self.prev_net.bytes_sent) / elapsed,
                "bytes_recv_per_s": (current_net_io.bytes_recv - self.prev_net.bytes_recv) / elapsed,
            }
        }

        # update refs
        self.prev_disk = current_disk_io
        self.prev_net = current_net_io
        self.prev_time = now
        return metrics

    async def run(self):
        async with httpx.AsyncClient(timeout=10.0) as client:
            while True:
                metrics = self.collect_metrics()
                payload = {
                    "client_id": self.client_id,
                    "metrics": metrics,
                    "timestamp": time.time(),
                }
                try:
                    r = await client.post(self.server_url, json=payload)
                    if r.status_code != 200:
                        print(f"[WARN] envio falhou: {r.status_code} {r.text}")
                    else:
                        print(f"[INFO] enviado {time.strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    print(f"[ERROR] ao enviar métricas: {e}")
                await asyncio.sleep(self.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente de coleta de métricas")
    parser.add_argument("--id", help="client id", default=None)
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--server", default="http://127.0.0.1:8000/ingest")
    args = parser.parse_args()

    agent = MonitoringAgent(client_id=args.id, interval=args.interval, server_url=args.server)
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("Agent encerrado")
