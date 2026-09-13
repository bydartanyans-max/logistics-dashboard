import os
import tempfile

import pytest

import app as logistics


@pytest.fixture()
def client(monkeypatch):
    fd, db_path = tempfile.mkstemp()
    os.close(fd)

    monkeypatch.setattr(logistics, "DB_PATH", logistics.Path(db_path))
    logistics.app.config.update(TESTING=True)
    logistics.init_db()

    with logistics.app.test_client() as test_client:
        yield test_client

    os.unlink(db_path)


def create_delivery(client, **overrides):
    payload = {
        "customer": "Demo Store",
        "destination": "Iasi",
        "driver": "Alex",
        "status": "planned",
    }
    payload.update(overrides)
    return client.post("/api/deliveries", json=payload)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_delivery(client):
    response = create_delivery(client)
    assert response.status_code == 201
    data = response.get_json()
    assert data["customer"] == "Demo Store"
    assert data["status"] == "planned"


def test_reject_invalid_status(client):
    response = create_delivery(client, status="unknown")
    assert response.status_code == 400


def test_update_status_and_driver(client):
    delivery_id = create_delivery(client).get_json()["id"]
    response = client.patch(
        f"/api/deliveries/{delivery_id}",
        json={"status": "in_transit", "driver": "Maria"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "in_transit"
    assert data["driver"] == "Maria"


def test_filter_and_summary(client):
    create_delivery(client, status="planned", driver="Alex")
    create_delivery(client, status="delivered", driver="Maria")

    filtered = client.get("/api/deliveries?status=delivered")
    assert filtered.status_code == 200
    assert len(filtered.get_json()) == 1

    summary = client.get("/api/summary")
    assert summary.status_code == 200
    data = summary.get_json()
    assert data["total"] == 2
    assert data["delivered"] == 1
    assert data["planned"] == 1
