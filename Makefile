
.PHONY: infra-up infra-down run-gateway run-agent run-worker-cart run-gmaas

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down -v

run-gateway:
	uvicorn services.gateway.main:app --reload --host 0.0.0.0 --port 8000

run-agent:
	uvicorn services.agent_core.main:app --reload --host 0.0.0.0 --port 8001

run-worker-cart:
	python -m services.workers.cart.worker

run-gmaas:
	uvicorn services.gmaas.main:app --reload --host 0.0.0.0 --port 8003
