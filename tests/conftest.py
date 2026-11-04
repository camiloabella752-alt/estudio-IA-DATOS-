import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test_orders.db")
os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("REDIS_URL", "redis://redis:6379/0")

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fakeredis import FakeStrictRedis  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from rq import Queue  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from estudio_ia_datos.api import app  # noqa: E402
from estudio_ia_datos.db import engine  # noqa: E402
from estudio_ia_datos.queue import get_queue  # noqa: E402

_redis_falso = FakeStrictRedis()


def _cola_de_prueba() -> Queue:
    return Queue("pedidos", connection=_redis_falso, is_async=False)


app.dependency_overrides[get_queue] = _cola_de_prueba

@pytest.fixture
def client() -> Iterator[TestClient]:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c

