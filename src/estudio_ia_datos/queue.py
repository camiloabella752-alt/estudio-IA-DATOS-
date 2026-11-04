import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_queue() -> Queue:
    return Queue("pedidos", connection=Redis.from_url(REDIS_URL))