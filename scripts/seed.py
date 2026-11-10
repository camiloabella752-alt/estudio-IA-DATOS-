"""Genera pedidos sintéticos en la tabla pedidos_raw. Uso: uv run scripts/seed.py"""

import os
import random
from datetime import date, datetime, time, timedelta

import psycopg
from faker import Faker

DSN = os.getenv("SEED_DSN", "postgresql://estudio:estudio123@localhost:5432/pedidos")
N = int(os.getenv("SEED_N", "5000"))

random.seed(42)
Faker.seed(42)
fake = Faker("es_CO")

PRODUCTOS = [
    "leche", "arroz", "azucar", "aceite", "huevos", "papa", "sal", "pan", "cafe", "panela",
    "frijol", "lenteja", "pasta", "atun", "gaseosa", "agua", "jabon", "detergente", "papel",
    "shampoo", "galletas", "chocolate", "harina", "avena", "queso", "mantequilla", "yogur",
    "salchicha", "jamon", "cerveza",
]


def main() -> None:
    clientes = [(i, fake.company(), fake.city()) for i in range(1, 51)]
    productos = [(i, nombre, random.randrange(1500, 60000, 100)) for i, nombre in enumerate(PRODUCTOS, 1)]
    inicio = date.today() - timedelta(days=365)

    filas = []
    for _ in range(N):
        cid, cliente, ciudad = random.choice(clientes)
        pid, producto, precio = random.choice(productos)
        cantidad = random.randint(1, 20)
        fecha = inicio + timedelta(days=random.randint(0, 364))
        creado = datetime.combine(fecha, time(random.randint(6, 20), random.randint(0, 59)))
        filas.append((cid, cliente, ciudad, pid, producto, cantidad, precio, cantidad * precio, fecha, creado))

    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS pedidos_raw")
        cur.execute(
            """
            CREATE TABLE pedidos_raw (
                id serial PRIMARY KEY,
                cliente_id int, cliente text, ciudad text,
                producto_id int, producto text,
                cantidad int, precio_unitario numeric, total numeric,
                fecha date, creado_en timestamp
            )
            """
        )
        with cur.copy(
            "COPY pedidos_raw (cliente_id, cliente, ciudad, producto_id, producto, cantidad, "
            "precio_unitario, total, fecha, creado_en) FROM STDIN"
        ) as copy:
            for fila in filas:
                copy.write_row(fila)
    print(f"Insertadas {N} filas en pedidos_raw")


if __name__ == "__main__":
    main()