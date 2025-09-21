import os
import asyncpg
from contextlib import asynccontextmanager
from app.core.config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_SSL_MODE,
    DB_POOL_MIN, DB_POOL_MAX, DB_TIMEOUT,
)
import ssl as ssl_lib

# Global pool for app
DB_POOL = None
# Separate pool for tests
_TEST_POOL = None

# App pool
async def init_db_pool():
    """Initialize the main app pool."""
    global DB_POOL
    if DB_POOL:
        return DB_POOL

    ssl_mode = os.getenv("DB_SSL_MODE", DB_SSL_MODE).lower()
    ssl = None
    if ssl_mode != "disable":
        ssl = ssl_lib.create_default_context()

    DB_POOL = await asyncpg.create_pool(
        user=os.getenv("DB_USER", DB_USER),
        password=os.getenv("DB_PASSWORD", DB_PASSWORD),
        host=os.getenv("DB_HOST", DB_HOST),
        port=int(os.getenv("DB_PORT", DB_PORT)),
        database=os.getenv("DB_NAME", DB_NAME),
        min_size=int(os.getenv("DB_POOL_MIN", DB_POOL_MIN)),
        max_size=int(os.getenv("DB_POOL_MAX", DB_POOL_MAX)),
        command_timeout=int(os.getenv("DB_TIMEOUT", DB_TIMEOUT)),
        ssl=ssl,
    )
    return DB_POOL

async def close_db_pool():
    global DB_POOL
    if DB_POOL:
        await DB_POOL.close()
        DB_POOL = None

@asynccontextmanager
async def db_conn():
    """Context manager for a single connection from the main pool."""
    if not DB_POOL:
        raise RuntimeError("DB pool not initialized. Call init_db_pool() on startup.")
    async with DB_POOL.acquire() as conn:
        yield conn

# Test pool
async def init_test_pool():
    """Initialize the test pool (single session-scoped pool)."""
    global _TEST_POOL
    if _TEST_POOL:
        return _TEST_POOL

    _TEST_POOL = await asyncpg.create_pool(
        user=os.getenv("DB_USER", DB_USER),
        password=os.getenv("DB_PASSWORD", DB_PASSWORD),
        host=os.getenv("DB_HOST", DB_HOST),
        port=int(os.getenv("DB_PORT", DB_PORT)),
        database=os.getenv("DB_NAME", DB_NAME),
        min_size=1,
        max_size=5,
        command_timeout=10,
        ssl=False,
    )
    return _TEST_POOL

async def close_test_pool():
    global _TEST_POOL
    if _TEST_POOL:
        await _TEST_POOL.close()
        _TEST_POOL = None

@asynccontextmanager
async def get_test_db_conn(pool):
    """Context manager for a single test DB connection."""
    async with pool.acquire() as conn:
        yield conn