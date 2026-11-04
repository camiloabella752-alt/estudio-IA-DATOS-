import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test_orders.db")
os.environ.setdefault("API_KEY", "test-key")

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from estudio_ia_datos.api import app  # noqa: E402
from estudio_ia_datos.db import engine  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c