from fastapi.testclient import TestClient

HEADERS = {"X-API-Key": "test-key"}


def test_crear_y_leer_pedido(client: TestClient) -> None:
    r = client.post(
        "/orders", json={"text": "3 cajas de leche", "cliente": "Tienda X"}, headers=HEADERS
    )
    assert r.status_code == 201
    creado = r.json()
    assert creado["items"][0]["producto"] == "leche"
    assert creado["items"][0]["cantidad"] == 3

    r2 = client.get(f"/orders/{creado['id']}", headers=HEADERS)
    assert r2.status_code == 200
    assert r2.json()["cliente"] == "Tienda X"


def test_pedido_no_existe(client: TestClient) -> None:
    assert client.get("/orders/9999", headers=HEADERS).status_code == 404


def test_sin_api_key(client: TestClient) -> None:
    r = client.post("/orders", json={"text": "3 cajas de leche", "cliente": "X"})
    assert r.status_code == 401


def test_texto_sin_productos(client: TestClient) -> None:
    r = client.post("/orders", json={"text": "hola buenas", "cliente": "X"}, headers=HEADERS)
    assert r.status_code == 422


def test_listar_con_paginacion(client: TestClient) -> None:
    for i in range(3):
        client.post(
            "/orders", json={"text": f"{i + 1} cajas de leche", "cliente": "Tienda X"}, headers=HEADERS
        )
    r = client.get("/orders?cliente=Tienda%20X&limit=2&offset=0", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 2