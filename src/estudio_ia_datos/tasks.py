import json
import os
import random

from sqlmodel import Session

from estudio_ia_datos.db import OrderRecord, engine
from estudio_ia_datos.orders import parse_order

FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))


def procesar_pedido(text: str, cliente: str) -> int:
    """Parsea y guarda un pedido. Devuelve el id creado."""
    if random.random() < FAIL_RATE:
        raise RuntimeError("Fallo simulado del worker")
    pedido = parse_order(text, cliente=cliente)
    record = OrderRecord(
        cliente=pedido.cliente,
        fecha=pedido.fecha,
        items_json=json.dumps([i.model_dump() for i in pedido.items]),
        texto_original=text,
    )
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.id or 0