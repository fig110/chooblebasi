# Windows Quickstart (CMD) — AI Shopping Platform v3

Use these helpers from the **repo root** (the folder that contains `services/` and `infra/`).

## 0) Prereqs
- Docker Desktop running (WSL2 enabled)
- Python 3.x in PATH

## 1) First‑time setup
Double‑click:
```
scripts\cmd\setup.bat
```

## 2) Start infrastructure
```
scripts\cmd\infra-up.bat
```

## 3) Start the app services
Start all at once:
```
scripts\cmd\run-all.bat
```
Or individually:
```
scripts\cmd\run-gateway.bat
scripts\cmd\run-agent.bat
scripts\cmd\run-worker-cart.bat
scripts\cmd\run-gmaas.bat
```

## 4) Health checks
- Gateway: http://localhost:8000/healthz
- Agent:   http://localhost:8001/healthz
- GMaaS:   http://localhost:8003/healthz
- RabbitMQ UI: http://localhost:15672 (guest/guest)

## 5) WebSocket smoke test
Use any WebSocket tester (Postman, "WebSocket King", etc.).
- URL: `ws://localhost:8000/ws/demo-session`
- Message:
```
{"user_id": "u_1", "text": "add a blue jacket to my cart"}
```

## 6) Stop infrastructure
```
scripts\cmd\infra-down.bat
```
