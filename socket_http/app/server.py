from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from collections import deque
import asyncio
import time
import json


class IngestPayload(BaseModel):
    client_id: str
    metrics: dict
    timestamp: float | None = None


class MonitoringServer:
    def __init__(self, metrics_window: int = 1000, sse_queue_size: int = 100):
        self.app = FastAPI(title="Monitoring HTTP Server")

        # config
        self.metrics_window = metrics_window
        self.sse_queue_size = sse_queue_size

        # storage
        self.clients = {}  # client_id -> {"last_seen": timestamp}
        self.metrics_store = {}  # client_id -> deque of metrics
        self.subscribers = set()  # asyncio.Queue por subscriber
        self.subscribers_lock = asyncio.Lock()

        # rotas
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/ingest")
        async def ingest(payload: IngestPayload):
            ts = payload.timestamp or time.time()
            entry = {
                "client_id": payload.client_id,
                "metrics": payload.metrics,
                "timestamp": ts,
            }

            # update client info
            self.clients[payload.client_id] = {"last_seen": ts}

            # append metrics
            if payload.client_id not in self.metrics_store:
                self.metrics_store[payload.client_id] = deque(maxlen=self.metrics_window)
            self.metrics_store[payload.client_id].append(entry)

            # broadcast SSE
            asyncio.create_task(self.broadcast_event(entry))
            return JSONResponse({"status": "ok"})

        @self.app.get("/clients")
        async def list_clients():
            return JSONResponse(
                [{"client_id": cid, "last_seen": info["last_seen"]}
                 for cid, info in self.clients.items()]
            )

        @self.app.get("/metrics/{client_id}")
        async def get_metrics(client_id: str, n: int = 50):
            if client_id not in self.metrics_store:
                return JSONResponse({"error": "client not found"}, status_code=404)
            data = list(self.metrics_store[client_id])[-n:]
            return JSONResponse(data)

        @self.app.get("/stream")
        async def stream(request: Request):
            q = asyncio.Queue(maxsize=self.sse_queue_size)
            async with self.subscribers_lock:
                self.subscribers.add(q)

            async def event_generator():
                try:
                    while True:
                        if await request.is_disconnected():
                            break
                        try:
                            data = await q.get()
                        except asyncio.CancelledError:
                            break
                        yield f"data: {data}\n\n"
                finally:
                    async with self.subscribers_lock:
                        self.subscribers.discard(q)

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        @self.app.get("/health")
        async def health():
            return JSONResponse({"status": "ok"})

    async def broadcast_event(self, entry: dict):
        payload = json.dumps(entry, default=str)
        async with self.subscribers_lock:
            to_remove = []
            for q in list(self.subscribers):
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    to_remove.append(q)
            for q in to_remove:
                self.subscribers.remove(q)


# instância padrão
monitoring_server = MonitoringServer()
app = monitoring_server.app
