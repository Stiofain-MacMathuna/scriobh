import os
import asyncpg
import ssl as ssl_lib
import asyncio
from contextlib import asynccontextmanager
from app.core.config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_SSL_MODE,
    DB_POOL_MIN, DB_POOL_MAX, DB_TIMEOUT,
)

DB_POOL = None
_TEST_POOL = None

# Retry logic for pool initialization
async def init_db_pool(retries=3, delay=2):
    """Initialize the main app pool with retry support."""
    global DB_POOL
    if DB_POOL:
        return DB_POOL

    ssl_mode = os.getenv("DB_SSL_MODE", DB_SSL_MODE).lower()
    ssl = None
    if ssl_mode != "disable":
        ssl = ssl_lib.create_default_context()

    for attempt in range(retries):
        try:
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
            print(f"✅ DB pool initialized: max={DB_POOL._maxsize}")
            return DB_POOL
        except Exception as e:
            print(f"❌ DB pool init failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(delay)

    raise RuntimeError("Failed to initialize DB pool after retries.")

async def close_db_pool():
    global DB_POOL
    if DB_POOL:
        await DB_POOL.close()
        DB_POOL = None

@asynccontextmanager
async def db_conn(timeout=10):
    """Context manager for a single connection from the main pool."""
    if not DB_POOL:
        raise RuntimeError("DB pool not initialized. Call init_db_pool() on startup.")
    try:
        async with DB_POOL.acquire(timeout=timeout) as conn:
            yield conn
    except Exception as e:
        print(f"❌ DB connection acquisition failed: {e}")
        raise

# Optional: expose pool metrics for health checks
def get_pool_status():
    if not DB_POOL:
        return {"initialized": False}
    return {
        "initialized": True,
        "max_size": DB_POOL._maxsize,
        "used": DB_POOL._used,
        "free": DB_POOL._queue.qsize(),
        "waiting": len(DB_POOL._holders) - DB_POOL._used,
    }

# Test pool
async def init_test_pool():
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
    async with pool.acquire() as conn:
        yield conn