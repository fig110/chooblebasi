import pika, json, threading, time
from typing import Callable, Optional

class Bus:
    def __init__(self, amqp_url: str):
        params = pika.URLParameters(amqp_url)
        self._conn = pika.BlockingConnection(params)
        self._chan = self._conn.channel()
        self._chan.confirm_delivery()

    def declare(self, queue: str, durable: bool = True):
        self._chan.queue_declare(queue=queue, durable=durable)

    def publish(self, queue: str, message: dict, persistent: bool = True):
        body = json.dumps(message).encode("utf-8")
        props = pika.BasicProperties(delivery_mode=2 if persistent else 1)
        self._chan.basic_publish("", routing_key=queue, body=body, properties=props, mandatory=True)

    def consume(self, queue: str, handler: Callable[[dict], None]):
        def _on_msg(ch, method, props, body):
            try:
                payload = json.loads(body.decode("utf-8"))
                handler(payload)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                # Nack with requeue=false -> sends to DLQ if bound
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self._chan.basic_qos(prefetch_count=10)
        self._chan.basic_consume(queue=queue, on_message_callback=_on_msg)
        self._chan.start_consuming()
