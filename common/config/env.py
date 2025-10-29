from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # RabbitMQ
    amqp_url: str = Field(default="amqp://guest:guest@localhost:5672/%2F")
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    # Service ports (for reference)
    gateway_port: int = 8000
    agent_port: int = 8001
    gmaas_port: int = 8003

settings = Settings()
