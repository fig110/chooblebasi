# AI Shopping Platform v3 — Starter Repo

This repository now contains **two side-by-side implementations**:

1. **Legacy FastAPI/RabbitMQ skeleton** (contracts-first, event-driven) – kept intact for future phases.
2. **New Django/Telegram monolith (Phase 1)** – the current focus for a Telegram-only AI shopping copilot using Postgres, Redis,
   and Dramatiq.

## Repository layout

- `services/` – legacy FastAPI services (`gateway`, `agent_core`, `workers`, `gmaas`).
- `infra/` – Docker Compose for Postgres, Redis, RabbitMQ (supports both stacks).
- `common/` – shared Pydantic schemas and messaging helpers for the legacy stack.
- `services/ai_shop_django/` – **new Django project** for the Phase 1 Telegram experience.

## Running the Phase 1 Django + Telegram stack

### Prerequisites
- Python 3.11+
- Postgres and Redis running locally (or via `make infra-up`). Defaults: `postgres://shopping:shopping@localhost:5432/shopping`,
  Redis at `redis://localhost:6379/0`.
- A Telegram bot token (from BotFather) and a webhook URL you control.

### Environment
Set these environment variables (e.g., in a `.env` file or inline before commands):

- `DJANGO_SECRET_KEY` – any non-empty string for local dev.
- `TELEGRAM_BOT_TOKEN` – your bot token from BotFather.
- `TG_WEBHOOK_SECRET` – an arbitrary secret included in the webhook path (e.g., `my-secret-slug`).
- `POSTGRES_*` and `REDIS_URL` if you are not using the defaults above.
- `DJANGO_SETTINGS_MODULE` (optional) – defaults to `ai_shop.settings.local`.

### Setup and migrate
```bash
pip install -r requirements.txt
make django-migrate
```

### Run Django API (and Redis/Dramatiq)
```bash
make run-django        # serves on http://0.0.0.0:8080
make run-django-worker # Dramatiq worker (needs Redis running)
```
Health check: `GET http://localhost:8080/healthz/`.

If you need local Redis/Postgres, `make infra-up` will start them via Docker Compose.

### Configure the Telegram webhook
Point Telegram to your webhook URL:
```
https://<your-host>/telegram/webhook/<TG_WEBHOOK_SECRET>/
```
Telegram will POST updates here; the view enqueues `run_agent_turn` and responds immediately with `{ "ok": true }`.

### What the vertical slice does today
- Receives Telegram text messages at the webhook.
- Transforms them into platform-agnostic `MessageIn` DTOs.
- Enqueues `run_agent_turn` via Dramatiq.
- Runs an `AgentRuntime` that records the conversation, detects basic shopping intents, and replies via Telegram with product search and cart actions.

### How to test product + cart flows quickly
1. Start Django, Redis, and the Dramatiq worker (see above).
2. Create a few products (via Django admin or shell):
   ```bash
   python services/ai_shop_django/manage.py shell -c "from ai_shop.apps.products.models import Product; Product.objects.create(name='Blue Jacket', price='59.99'); Product.objects.create(name='Sneakers', price='89.00', category='shoes')"
   ```
3. Message your Telegram bot:
   - "show me jackets" → returns product suggestions with IDs.
   - "add 1" or "add product 1" → adds by product ID.
   - "what's in my cart?" → displays current cart contents and totals.
   - "remove 1" → drops the product from your cart.

The same flow works with `curl` by POSTing Telegram-style updates to `/telegram/webhook/<TG_WEBHOOK_SECRET>/`.

## Legacy FastAPI/RabbitMQ skeleton (unchanged)

The original event-driven starter remains available:

1. Start infra:
   ```bash
   make infra-up
   ```
2. In separate terminals:
   ```bash
   make run-gateway
   make run-agent
   make run-worker-cart
   make run-gmaas
   ```
3. Health check: `GET http://localhost:8000/healthz`.
4. WebSocket demo: connect to `ws://localhost:8000/ws/demo-session` and send `{ "user_id": "u_1", "text": "add a blue jacket to my cart" }`.

----------
For information on how to run the legacy scripts read the following: `scripts/cmd/README.md`.
