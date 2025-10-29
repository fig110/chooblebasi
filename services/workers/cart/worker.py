from common.messaging.rabbit import Bus
from common.schemas.tools import AddToCartRequest, AddToCartResponse
from common.config.env import settings
import redis, uuid

bus = Bus(settings.amqp_url)
r = redis.from_url(settings.redis_url, decode_responses=True)

def _idempotent(key: str, value: str) -> bool:
    # Returns True if this is a new operation; False if duplicate
    return r.setnx(f"idempotency:{key}", value)

def handle_add_to_cart(payload: dict):
    req = AddToCartRequest(**payload)
    # Idempotency
    if not _idempotent(req.idempotency_key, req.correlation_id):
        # Duplicate, just drop (or return prior result)
        return

    # Simulate adding a line item
    line_id = str(uuid.uuid4())
    resp = AddToCartResponse(
        correlation_id=req.correlation_id,
        cart_id=req.cart_id,
        line_id=line_id,
        status="OK",
        message="Item added"
    )
    # Publish response
    bus.declare("tool.response.cart.add_item")
    bus.publish("tool.response.cart.add_item", resp.model_dump())

def _consume():
    bus.declare("tool.request.cart.add_item")
    bus.consume("tool.request.cart.add_item", handle_add_to_cart)

if __name__ == "__main__":
    _consume()
