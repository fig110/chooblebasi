# AI Shopping Platform v3 — Starter Repo

This is a **minimal, runnable starter** for the event-driven, contracts-first architecture we discussed.
It favors **practicality** and **clarity**: FastAPI for HTTP/WS services, RabbitMQ for the bus, Redis for working memory/idempotency,
Postgres for data, and Pydantic models for contracts.

> Note: This is a skeleton focused on wiring and contracts. You’ll flesh out business logic, LangGraph flows, and catalog/RAG later.

## What’s included
- **Contracts-first** Pydantic models exported to JSON Schema
- **Gateway (BFF)** with WebSocket streaming & health endpoint
- **Agent Core** skeleton that routes user input to tool requests and streams replies
- **Cart Worker** that consumes `tool.request.cart.add_item` and replies with `tool.response.cart.add_item` (idempotent)
- **GMaaS** stub for async media jobs
- **Messaging** utils for RabbitMQ (pika)
- **Infra** via Docker Compose: RabbitMQ, Redis, Postgres

## Quick start

1) Start infra:
```bash
make infra-up
```

2) In separate terminals (or use a process manager), run services:

```bash
# Terminal A
make run-gateway

# Terminal B
make run-agent

# Terminal C
make run-worker-cart

# Terminal D
make run-gmaas
```

3) Hit health checks:
- Gateway: `GET http://localhost:8000/healthz`

4) Connect a WS client to: `ws://localhost:8000/ws/demo-session`
Send JSON: `{"user_id":"u_1","text":"add a blue jacket to my cart"}` and watch the flow.

## Notes
- Env defaults assume `localhost` for infra.
- Replace the naive agent router with LangGraph + proper intents.
- Wire Postgres and vector DB as you flesh out catalog, RAG, and checkout.
- This repo aims to **unblock the first end-to-end loop** with contracts + bus + async workers.
