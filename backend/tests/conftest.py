import uuid
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.main import app
from app.db import init_test_pool, close_test_pool, get_test_db_conn, init_test_pool
from app.core import security as auth_module
from httpx import ASGITransport
from tests.constants import TEST_EMAIL, TEST_PASSWORD, FIXED_USER_ID

# --- Function-scoped test pool ---
@pytest.fixture(scope="function")
async def test_pool():
    pool = await init_test_pool()
    yield pool
    await close_test_pool()

# Override auth globally
@pytest.fixture(scope="session", autouse=True)
def override_auth_dependency():
    app.dependency_overrides[auth_module.get_current_user_id] = lambda: FIXED_USER_ID
    yield
    app.dependency_overrides.clear()

# Async test client
@pytest.fixture(scope="function")
async def async_test_client(test_pool):
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

# Cleanup notes after each test
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
        await conn.execute("DELETE FROM users WHERE email = $1", TEST_EMAIL)
        await conn.execute("""
            INSERT INTO users (id, email, password_hash)
            VALUES ($1, $2, $3)
        """, FIXED_USER_ID, TEST_EMAIL, auth_module.hash_password(TEST_PASSWORD))
    yield
