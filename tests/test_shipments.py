import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from stage3_systems.database import Base, get_db
from stage3_systems.main import app


@pytest.fixture
def client():
    # Use a temporary in-memory database for these tests.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_create_and_retrieve_shipment(client):
    order = {
        "customer": "Test Customer",
        "origin": "Dodoma",
        "destination": "Dar es Salaam",
        "weight_kg": 3,
        "service": "standard",
    }

    create_response = client.post("/shipments/", json=order)

    assert create_response.status_code == 201

    created = create_response.json()
    shipment_id = created["shipment_id"]

    assert created["customer"] == "Test Customer"
    assert created["price_tzs"] == 7150
    assert created["status"] == "Booked"

    get_response = client.get(f"/shipments/{shipment_id}")

    assert get_response.status_code == 200
    assert get_response.json()["shipment_id"] == shipment_id


def test_invalid_weight_is_rejected(client):
    order = {
        "customer": "Test Customer",
        "origin": "Dodoma",
        "destination": "Dar es Salaam",
        "weight_kg": -1,
        "service": "standard",
    }

    response = client.post("/shipments/", json=order)

    assert response.status_code == 422


def test_unknown_shipment_returns_404(client):
    response = client.get("/shipments/SL99999")

    assert response.status_code == 404


def test_shipment_status_can_be_updated(client):
    order = {
        "customer": "Test Customer",
        "origin": "Dodoma",
        "destination": "Dar es Salaam",
        "weight_kg": 3,
        "service": "standard",
    }

    created = client.post("/shipments/", json=order).json()
    shipment_id = created["shipment_id"]

    response = client.patch(
        f"/shipments/{shipment_id}/status",
        json={"status": "In Transit"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Transit"