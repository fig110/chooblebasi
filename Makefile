
.PHONY: infra-up infra-down run-gateway run-agent run-worker-cart run-gmaas run-django run-django-worker django-migrate

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

run-django:
python services/ai_shop_django/manage.py runserver 0.0.0.0:8080

run-django-worker:
python services/ai_shop_django/manage.py rundramatiq ai_shop.apps.agent_tasks

django-migrate:
python services/ai_shop_django/manage.py migrate
