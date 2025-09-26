import pytest
import pytest_asyncio
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# Load test environment variables from backend/.env.test
dotenv_path = Path(__file__).parent / ".env.test"
load_dotenv(dotenv_path, override=True)

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from app.main import app
from app.db import init_test_pool, close_test_pool, get_test_db_conn
from app.core import security as auth_module
from app.core.security import get_current_user_id
from tests.constants import TEST_EMAIL, TEST_PASSWORD, FIXED_USER_ID

print("conftest.py loaded")

# Run Alembic migrations once before all tests
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    print("Running Alembic migrations before tests...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)

@pytest_asyncio.fixture(scope="function")
async def test_pool():
    pool = await init_test_pool()
    yield pool
    await close_test_pool()

@pytest_asyncio.fixture(scope="function")
async def async_test_client(test_pool):
    app.dependency_overrides[get_current_user_id] = lambda: FIXED_USER_ID
    print("Applied override inside async_test_client")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    app.dependency_overrides.clear()
    print("Cleared override after test")

@pytest_asyncio.fixture
async def cleanup_notes(test_pool):
    async with get_test_db_conn(test_pool) as conn:
        await conn.execute("DELETE FROM notes WHERE user_id = $1", FIXED_USER_ID)
    yield

@pytest_asyncio.fixture
async def cleanup_user(test_pool):
    async with test_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", "auth_test@example.com")
    yield
    async with test_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", "auth_test@example.com")

@pytest_asyncio.fixture
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