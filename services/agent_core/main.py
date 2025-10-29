from fastapi import FastAPI
from fastapi.responses import JSONResponse
from common.config.env import settings
from common.messaging.rabbit import Bus
from common.schemas.events import UserInputEvent, AgentOutputEvent, Fragment
from common.schemas.tools import AddToCartRequest, AddToCartResponse
import threading, time, uuid, json, redis

app = FastAPI(title="Agent Core")
bus = Bus(settings.amqp_url)
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})

def _handle_user_input(payload: dict):
    # Validate envelope
    evt = UserInputEvent(**payload)
    text = (evt.text or "").lower()

    # Very naive routing: look for "add" and fake a product
    if "add" in text and "cart" in text:
        tool_req = AddToCartRequest(
            correlation_id=evt.correlation_id,
            idempotency_key=f"{evt.session_id}|demo|{int(time.time())}",
            user_id=evt.user_id,
            cart_id=f"cart-{evt.user_id}",
            product_id="demo-product-001",
            quantity=1
        )
        bus.declare("tool.request.cart.add_item")
        bus.publish("tool.request.cart.add_item", tool_req.model_dump())
        # Stream a partial to the client via Redis (gateway will poll; in real, push WS directly)
        frag = Fragment(type="text", content="Sure—adding that to your cart…")
        out = AgentOutputEvent(correlation_id=evt.correlation_id, session_id=evt.session_id, fragments=[frag])
        redis_client.rpush(f"agent:out:{evt.session_id}", out.model_dump_json())
    else:
        # Simple echo/help
        frag = Fragment(type="text", content="Try: 'add a blue jacket to my cart'")
        out = AgentOutputEvent(correlation_id=evt.correlation_id, session_id=evt.session_id, fragments=[frag])
        redis_client.rpush(f"agent:out:{evt.session_id}", out.model_dump_json())

def _consumer_loop():
    bus.declare("user.input")
    bus.consume("user.input", _handle_user_input)

# Run consumer in background thread
import threading
threading.Thread(target=_consumer_loop, daemon=True).start()
