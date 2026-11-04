import os
from collections.abc import Iterator
from datetime import date

from sqlmodel import Field, Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///orders.db")
engine = create_engine(DATABASE_URL)


class OrderRecord(SQLModel, table=True):
    """Fila de la tabla de pedidos."""

    id: int | None = Field(default=None, primary_key=True)
    cliente: str
    fecha: date
    items_json: str
    texto_original: str

class IdempotencyKey(SQLModel, table=True):
    """Relaciona una Idempotency-Key con el job que la atendió."""

    key: str = Field(primary_key=True)
    job_id: str


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session