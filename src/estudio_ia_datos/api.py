import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from rq import Queue, Retry
from rq.exceptions import NoSuchJobError
from rq.job import Job
from sqlmodel import Session, select

from estudio_ia_datos.db import IdempotencyKey, OrderRecord, create_tables, get_session
from estudio_ia_datos.orders import Item
from estudio_ia_datos.queue import get_queue
from estudio_ia_datos.tasks import procesar_pedido

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

class JobOut(BaseModel):
    job_id: str
    status: str
    order_id: int | None = None

def verificar_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida o ausente")


def a_salida(record: OrderRecord) -> OrderOut:
    items = [Item(**i) for i in json.loads(record.items_json)]
    return OrderOut(id=record.id or 0, cliente=record.cliente, fecha=record.fecha, items=items)

def estado_job(job_id: str, queue: Queue) -> JobOut:
    try:
        job = Job.fetch(job_id, connection=queue.connection)
    except NoSuchJobError as e:
        raise HTTPException(status_code=404, detail="Job no encontrado") from e
    status = str(job.get_status())
    order_id = int(job.result) if status == "finished" and job.result is not None else None
    return JobOut(job_id=job.id, status=status, order_id=order_id)


@app.post("/orders", status_code=202, dependencies=[Depends(verificar_api_key)])
def crear_pedido(
    body: OrderIn,
    session: Session = Depends(get_session),
    queue: Queue = Depends(get_queue),
    idempotency_key: str | None = Header(default=None),
) -> JobOut:
    if idempotency_key:
        existente = session.get(IdempotencyKey, idempotency_key)
        if existente is not None:
            return estado_job(existente.job_id, queue)
    job = queue.enqueue(
        procesar_pedido,
        body.text,
        body.cliente,
        retry=Retry(max=3, interval=[2, 4, 8]),
    )
    if idempotency_key:
        session.add(IdempotencyKey(key=idempotency_key, job_id=job.id))
        session.commit()
    return estado_job(job.id, queue)


@app.get("/jobs/{job_id}", dependencies=[Depends(verificar_api_key)])
def leer_job(job_id: str, queue: Queue = Depends(get_queue)) -> JobOut:
    return estado_job(job_id, queue)


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