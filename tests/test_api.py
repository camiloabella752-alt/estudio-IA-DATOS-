from fastapi.testclient import TestClient

HEADERS = {"X-API-Key": "test-key"}


def test_crear_y_leer_pedido(client: TestClient) -> None:
    r = client.post(
        "/orders", json={"text": "3 cajas de leche", "cliente": "Tienda X"}, headers=HEADERS
    )
    assert r.status_code == 202
    job = r.json()
    assert job["status"] == "finished"
    assert job["order_id"] is not None

    r2 = client.get(f"/orders/{job['order_id']}", headers=HEADERS)
    assert r2.status_code == 200
    assert r2.json()["items"][0]["producto"] == "leche"


def test_idempotencia(client: TestClient) -> None:
    headers = {**HEADERS, "Idempotency-Key": "clave-abc"}
    body = {"text": "2 kg papa", "cliente": "Tienda X"}
    ids = {client.post("/orders", json=body, headers=headers).json()["job_id"] for _ in range(5)}
    assert len(ids) == 1
    pedidos = client.get("/orders?cliente=Tienda%20X", headers=HEADERS).json()
    assert len(pedidos) == 1


def test_job_no_existe(client: TestClient) -> None:
    assert client.get("/jobs/no-existe", headers=HEADERS).status_code == 404

def test_pedido_no_existe(client: TestClient) -> None:
    assert client.get("/orders/9999", headers=HEADERS).status_code == 404


def test_sin_api_key(client: TestClient) -> None:
    r = client.post("/orders", json={"text": "3 cajas de leche", "cliente": "X"})
    assert r.status_code == 401




def test_listar_con_paginacion(client: TestClient) -> None:
    for i in range(3):
        client.post(
            "/orders",
            json={"text": f"{i + 1} cajas de leche", "cliente": "Tienda X"},
            headers=HEADERS,
        )
    r = client.get("/orders?cliente=Tienda%20X&limit=2&offset=0", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 2
