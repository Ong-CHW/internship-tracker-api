import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestSession = sessionmaker(bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

@pytest.mark.parametrize("changes", [
    {"company": "   "},
    {"company": "X" * 101},
    {"status": "Unknown"},
    {"application_date": "not-a-date"},
    {"job_url": "this-is-not-a-url"}
])
def test_invalid_input(client, changes):
    response = client.post(
        "/applications",
        json=sample_application(**changes)
    )

    assert response.status_code == 422


def test_missing_company(client):
    data = sample_application()

    del data["company"]

    response = client.post(
        "/applications",
        json=data
    )

    assert response.status_code == 422

def sample_application(**changes):
    data = {
        "company": "Google",
        "position": "Software Engineering Intern",
        "status": "Applied",
        "application_date": "2026-09-25",
        "location": "Kuala Lumpur",
        "job_url": None,
        "notes": "Test application"
    }

    data.update(changes)

    return data

def test_create_and_get(client):
    response = client.post(
        "/applications",
        json=sample_application()
    )

    assert response.status_code == 201

    created = response.json()

    assert created["company"] == "Google"
    assert created["id"] == 1

    single = client.get(
        f"/applications/{created['id']}"
    )

    assert single.status_code == 200
    assert single.json()["company"] == "Google"

    all_apps = client.get("/applications")

    assert all_apps.status_code == 200
    assert len(all_apps.json()) == 1


def test_update(client):
    created = client.post(
        "/applications",
        json=sample_application()
    ).json()

    response = client.put(
        f"/applications/{created['id']}",
        json=sample_application(status="Interview")
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Interview"

    retrieved = client.get(
        f"/applications/{created['id']}"
    )

    assert retrieved.json()["status"] == "Interview"


def test_delete(client):
    created = client.post(
        "/applications",
        json=sample_application()
    ).json()

    response = client.delete(
        f"/applications/{created['id']}"
    )

    assert response.status_code == 204

    retrieved = client.get(
        f"/applications/{created['id']}"
    )

    assert retrieved.status_code == 404
    assert client.get("/applications").json() == []


def test_missing_ids(client):
    assert client.get("/applications/999").status_code == 404

    assert client.put(
        "/applications/999",
        json=sample_application()
    ).status_code == 404

    assert client.delete(
        "/applications/999"
    ).status_code == 404