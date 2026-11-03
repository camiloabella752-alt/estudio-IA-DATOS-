import re
from datetime import date

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Un producto dentro de un pedido."""

    producto: str = Field(min_length=1)
    cantidad: int = Field(gt=0)
    unidad: str | None = None


class Order(BaseModel):
    """Un pedido completo recibido por WhatsApp."""

    cliente: str = Field(min_length=1)
    items: list[Item] = Field(min_length=1)
    fecha: date


PATRON_ITEM = re.compile(
    r"(\d+)\s*(?:(cajas?|unidad(?:es)?|kgs?|litros?|bolsas?)\b)?\s*(?:de\s+)?([a-záéíóúñ]+)",
    re.IGNORECASE,
)


def parse_order(text: str, cliente: str = "desconocido", fecha: date | None = None) -> Order:
    """Convierte un mensaje como '3 cajas de leche y 2 de arroz' en un Order."""
    items = [
        Item(producto=producto.lower(), cantidad=int(cantidad), unidad=unidad.lower() or None)
        for cantidad, unidad, producto in PATRON_ITEM.findall(text)
    ]
    if not items:
        raise ValueError(f"No encontré ningún producto con cantidad en: {text!r}")
    return Order(cliente=cliente, items=items, fecha=fecha or date.today())