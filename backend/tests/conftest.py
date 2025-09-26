import os
import pytest
from dotenv import load_dotenv

# Load test environment variables
dotenv_path = os.path.join(os.getcwd(), "backend", ".env.test")
load_dotenv(dotenv_path, override=True)

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from app.main import app
from app.db import init_test_pool, close_test_pool, get_test_db_conn
from app.core import security as auth_module
from app.core.security import get_current_user_id
from tests.constants import TEST_EMAIL, TEST_PASSWORD, FIXED_USER_ID

print("conftest.py loaded")

@pytest.fixture(scope="function")
async def test_pool():
    pool = await init_test_pool()
    yield pool
    await close_test_pool()

@pytest.fixture(scope="function")
async def async_test_client(test_pool):
    # Apply auth override here after app is initialized
    app.dependency_overrides[get_current_user_id] = lambda: FIXED_USER_ID
    print("Applied override inside async_test_client")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    app.dependency_overrides.clear()
    print("Cleared override after test")

@pytest.fixture
async def cleanup_notes(test_pool):
    async with get_test_db_conn(test_pool) as conn:
        await conn.execute("DELETE FROM notes WHERE user_id = $1", FIXED_USER_ID)
    yield

@pytest.fixture
async def cleanup_user(test_pool):
    async with test_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", "auth_test@example.com")
    yield
    async with test_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", "auth_test@example.com")

@pytest.fixture
async def seed_auth_user(test_pool):
    async with test_pool.acquire() as conn:
        await conn.execute("DELETE FROM notes WHERE user_id = $1", FIXED_USER_ID)
        await conn.execute("DELETE FROM users WHERE email = $1", TEST_EMAIL)
        hashed_password = await auth_module.hash_password(TEST_PASSWORD)
        await conn.execute("""
            INSERT INTO users (id, email, password_hash)
            VALUES ($1, $2, $3)
        """, FIXED_USER_ID, TEST_EMAIL, hashed_password)
    yield