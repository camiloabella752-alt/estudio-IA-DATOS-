import pytest

from estudio_ia_datos.orders import parse_order


@pytest.mark.parametrize(
    "mensaje, esperado",
    [
        ("3 cajas de leche", [("leche", 3)]),
        ("3 cajas de leche y 2 de arroz", [("leche", 3), ("arroz", 2)]),
        ("Hola, mándame 5 kg papa para mañana", [("papa", 5)]),
        ("necesito 10 unidades de aceite", [("aceite", 10)]),
        ("1 caja de huevos", [("huevos", 1)]),
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