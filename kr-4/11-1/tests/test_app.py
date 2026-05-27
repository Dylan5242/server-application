import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
SPEC = importlib.util.spec_from_file_location("kr4_task_11_1_app", APP_PATH)
app_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = app_module
SPEC.loader.exec_module(app_module)

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def clean_state():
    app_module.reset_state()
    yield
    app_module.reset_state()


def test_create_user():
    response = client.post("/users", json={"username": "alice", "age": 25})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "alice", "age": 25}


def test_get_existing_user():
    created = client.post("/users", json={"username": "bob", "age": 30}).json()

    response = client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_user():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user():
    created = client.post("/users", json={"username": "carol", "age": 28}).json()

    response = client.delete(f"/users/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_user():
    response = client.delete("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_validation_error():
    response = client.post("/users", json={"username": "", "age": -1})

    assert response.status_code == 422
