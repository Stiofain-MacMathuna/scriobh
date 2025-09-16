import os
import asyncpg
from contextlib import asynccontextmanager
from app.core.config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_SSL_MODE,
    DB_POOL_MIN, DB_POOL_MAX, DB_TIMEOUT,
)

# Global pool for app
DB_POOL = None
# Separate pool for tests
_TEST_POOL = None

async def init_db_pool():
    """Initialize the main app pool."""
    global DB_POOL
    if DB_POOL:
        return DB_POOL

    ssl_mode = os.getenv("DB_SSL_MODE", DB_SSL_MODE).lower()
    ssl = False if ssl_mode == "disable" else True

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
async def db_conn():
    """Context manager for app DB connections."""
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn

@asynccontextmanager
async def get_test_db_conn(pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn