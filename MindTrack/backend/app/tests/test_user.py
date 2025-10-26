import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app, get_db, Base  # assumes app.main exposes get_db and Base

# Sample data (from data_schema.md)
SAMPLE_USER_1 = {"name": "Alice", "timezone": "UTC", "preferences": {"voice": "female", "speed": 1.0}}
SAMPLE_USER_2 = {"name": "Bob", "timezone": "Europe/London", "preferences": {"voice": "male", "speed": 0.9}}


@pytest.fixture
def client():
    """
    Create a test FastAPI app with an in-memory SQLite DB and yield a TestClient.
    """
    app = create_app()

    # In-memory SQLite DB for isolation
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create DB schema (assumes models are linked to Base)
    Base.metadata.create_all(bind=engine)

    # Dependency override to use the in-memory session
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as tc:
        yield tc


def test_create_user(client: TestClient):
    resp = client.post("/users", json=SAMPLE_USER_1)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "user_id" in data
    assert "created_at" in data
    assert data.get("name") == SAMPLE_USER_1["name"]


def test_get_user(client: TestClient):
    # create user
    create_resp = client.post("/users", json=SAMPLE_USER_1)
    assert create_resp.status_code == 201, create_resp.text
    user = create_resp.json()
    user_id = user["user_id"]

    # get user
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200, get_resp.text
    got = get_resp.json()
    assert got.get("user_id") == user_id
    assert got.get("name") == SAMPLE_USER_1["name"]
    assert got.get("preferences") == SAMPLE_USER_1["preferences"]


def test_list_users(client: TestClient):
    # create two users
    r1 = client.post("/users", json=SAMPLE_USER_1)
    r2 = client.post("/users", json=SAMPLE_USER_2)
    assert r1.status_code == 201 and r2.status_code == 201

    list_resp = client.get("/users")
    assert list_resp.status_code == 200, list_resp.text
    users = list_resp.json()
    # Expect at least the two created users
    names = {u.get("name") for u in users}
    assert SAMPLE_USER_1["name"] in names
    assert SAMPLE_USER_2["name"] in names


def test_validation_missing_fields(client: TestClient):
    # missing name
    bad_payload = {"timezone": "UTC", "preferences": {"voice": "female"}}
    resp = client.post("/users", json=bad_payload)
    assert resp.status_code == 422

    # missing timezone
    bad_payload = {"name": "NoTZ", "preferences": {}}
    resp = client.post("/users", json=bad_payload)
    assert resp.status_code == 422