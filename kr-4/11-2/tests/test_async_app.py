import importlib.util
import sys
from pathlib import Path

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
SPEC = importlib.util.spec_from_file_location("kr4_task_11_2_app", APP_PATH)
app_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = app_module
SPEC.loader.exec_module(app_module)

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def clean_state():
    app_module.reset_state()
    yield
    app_module.reset_state()


@pytest.fixture()
def fake_user():
    faker = Faker()
    return {
        "username": faker.user_name(),
        "age": faker.random_int(min=18, max=90),
    }


def get_client():
    transport = ASGITransport(app=app_module.app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_create_user(fake_user):
    async with get_client() as client:
        response = await client.post("/users", json=fake_user)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == fake_user["username"]
    assert data["age"] == fake_user["age"]


async def test_get_existing_user(fake_user):
    async with get_client() as client:
        created = (await client.post("/users", json=fake_user)).json()
        response = await client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_missing_user():
    async with get_client() as client:
        response = await client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_delete_existing_user(fake_user):
    async with get_client() as client:
        created = (await client.post("/users", json=fake_user)).json()
        response = await client.delete(f"/users/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""


async def test_repeated_delete_returns_404(fake_user):
    async with get_client() as client:
        created = (await client.post("/users", json=fake_user)).json()
        first_response = await client.delete(f"/users/{created['id']}")
        second_response = await client.delete(f"/users/{created['id']}")

    assert first_response.status_code == 204
    assert second_response.status_code == 404
    assert second_response.json()["detail"] == "User not found"


async def test_invalid_age_returns_422(fake_user):
    fake_user["age"] = -1

    async with get_client() as client:
        response = await client.post("/users", json=fake_user)

    assert response.status_code == 422
