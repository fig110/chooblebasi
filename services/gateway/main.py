from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio, json, time, uuid
import redis
from common.config.env import settings
from common.messaging.rabbit import Bus
from common.schemas.events import UserInputEvent, AgentOutputEvent, Fragment

app = FastAPI(title="Gateway")

r = redis.from_url(settings.redis_url, decode_responses=True)

@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})

# Simple WS hub per session (single process demo)
class WsHub:
    def __init__(self):
        self.connections = {}  # session_id -> websocket

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.connections[session_id] = ws

    async def disconnect(self, session_id: str):
        self.connections.pop(session_id, None)

    async def send(self, session_id: str, payload: dict):
        ws = self.connections.get(session_id)
        if ws:
            await ws.send_text(json.dumps(payload))

hub = WsHub()

@app.websocket("/ws/{session_id}")
async def ws_endpoint(ws: WebSocket, session_id: str):
    await hub.connect(session_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            # Prepare envelope and forward to agent input queue
            correlation_id = str(uuid.uuid4())
            event = UserInputEvent(
                correlation_id=correlation_id,
                causation_id=None,
                user_id=msg.get("user_id","anon"),
                session_id=session_id,
                text=msg.get("text"),
                timestamp=time.time()
            )
            # Publish to agent input queue
            bus = Bus(settings.amqp_url)
            bus.declare("user.input")
            bus.publish("user.input", event.model_dump())

            # Optimistic immediate feedback
            await hub.send(session_id, {"type": "ack", "correlation_id": correlation_id})
    except WebSocketDisconnect:
        await hub.disconnect(session_id)

# Simple poll endpoint for agent outputs (in real system, agent would push to WS directly)
@app.get("/poll/{session_id}")
async def poll(session_id: str):
    # fetch last N fragments from Redis list (demo)
    items = r.lrange(f"agent:out:{session_id}", 0, -1)
    return [json.loads(x) for x in items]
