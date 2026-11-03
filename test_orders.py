import pytest

from estudio_ia_datos.orders import parse_order


@pytest.mark.parametrize(
    "mensaje, esperado",
    [
        ("3 cajas de leche", [("leche", 3)]),
        ("3 cajas de leche y 2 de arroz", [("leche", 3), ("arroz", 2)]),
        ("Hola, mándame 5 kg papa para mañana", [("papa", 5)]),
        ("necesito 10 unidades de aceite", [("aceite", 10)]),
        ("1 caja de huevos", [("huevos", 2)]) ,
        ("2 de azucar, 4 de sal", [("azucar", 2), ("sal", 4)]),
    ],
)
def test_mensajes_validos(mensaje, esperado):
    pedido = parse_order(mensaje, cliente="Tienda X")
    assert [(i.producto, i.cantidad) for i in pedido.items] == esperado


@pytest.mark.parametrize(
    "mensaje",
    [
        "leche y arroz",
        "mándame leche por favor",
        "hola buenas tardes",
        "",
    ],
)
def test_mensajes_invalidos(mensaje):
    with pytest.raises(ValueError):
        parse_order(mensaje, cliente="Tienda X")

def test_captura_unidad():
    pedido = parse_order("3 cajas de leche y 2 kg papa", cliente="Tienda X")
    assert pedido.items[0].unidad == "cajas"
    assert pedido.items[1].unidad == "kg"


@pytest.mark.parametrize(
    "mensaje, producto, unidad",
    [
        ("2 bolsas", "bolsas", None),
        ("3 bolsas de pan", "pan", "bolsas"),
        ("1 unidad de aceite", "aceite", "unidad"),
        ("2 kgs de papa", "papa", "kgs"),
    ],
)
def test_unidad_palabra_completa(mensaje, producto, unidad):
    item = parse_order(mensaje, cliente="Tienda X").items[0]
    assert (item.producto, item.unidad) == (producto, unidad)
