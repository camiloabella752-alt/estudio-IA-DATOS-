import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from estudio_ia_datos.db import OrderRecord, create_tables, get_session
from estudio_ia_datos.orders import Item, parse_order

API_KEY = os.getenv("API_KEY", "dev-key-cambiame")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(title="Estudio IA Datos API", lifespan=lifespan)


class OrderIn(BaseModel):
    text: str
    cliente: str


class OrderOut(BaseModel):
    id: int
    cliente: str
    fecha: date
    items: list[Item]


def verificar_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida o ausente")


def a_salida(record: OrderRecord) -> OrderOut:
    items = [Item(**i) for i in json.loads(record.items_json)]
    return OrderOut(id=record.id or 0, cliente=record.cliente, fecha=record.fecha, items=items)


@app.post("/orders", status_code=201, dependencies=[Depends(verificar_api_key)])
def crear_pedido(body: OrderIn, session: Session = Depends(get_session)) -> OrderOut:
    try:
        pedido = parse_order(body.text, cliente=body.cliente)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    record = OrderRecord(
        cliente=pedido.cliente,
        fecha=pedido.fecha,
        items_json=json.dumps([i.model_dump() for i in pedido.items]),
        texto_original=body.text,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return a_salida(record)


@app.get("/orders/{order_id}", dependencies=[Depends(verificar_api_key)])
def leer_pedido(order_id: int, session: Session = Depends(get_session)) -> OrderOut:
    record = session.get(OrderRecord, order_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return a_salida(record)


@app.get("/orders", dependencies=[Depends(verificar_api_key)])
def listar_pedidos(
    cliente: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[OrderOut]:
    consulta = select(OrderRecord)
    if cliente:
        consulta = consulta.where(OrderRecord.cliente == cliente)
    registros = session.exec(consulta.offset(offset).limit(limit)).all()
    return [a_salida(r) for r in registros]