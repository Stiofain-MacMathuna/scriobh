import pytest
from app.core import security as auth_module
from tests.constants import TEST_EMAIL, TEST_PASSWORD, FIXED_USER_ID


@pytest.mark.asyncio
async def test_register_existing_user(async_test_client, seed_auth_user, cleanup_user):
    r = await async_test_client.post("/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 400
    assert r.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_existing_user(async_test_client, seed_auth_user):
    r = await async_test_client.post("/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 400
    assert r.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(async_test_client):
    r = await async_test_client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token is not None

@pytest.mark.asyncio
async def test_login_failure(async_test_client):
    r = await async_test_client.post("/auth/login", json={"email": TEST_EMAIL, "password": "wrongpass"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_me_endpoint(async_test_client, seed_auth_user):
    r = await async_test_client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    print("Login response:", r.status_code, r.json())
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = await async_test_client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == TEST_EMAIL
    assert data["id"] == str(FIXED_USER_ID)

