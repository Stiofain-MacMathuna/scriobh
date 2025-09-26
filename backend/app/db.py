import asyncio
import asyncpg
import ssl as ssl_lib
from contextlib import asynccontextmanager
from app.core.config import (
    get_db_user, get_db_password, get_db_host, get_db_port,
    get_db_name, get_db_ssl_mode, get_db_pool_min, get_db_pool_max,
    get_db_timeout
)

DB_POOL = None
_TEST_POOL = None

# Retry logic for pool initialization
async def init_db_pool(retries=3, delay=2):
    """Initialize the main app pool with retry support."""
    global DB_POOL
    if DB_POOL:
        return DB_POOL

    ssl_mode = get_db_ssl_mode().lower()
    ssl = None
    if ssl_mode != "disable":
        ssl = ssl_lib.create_default_context()

    for attempt in range(retries):
        try:
            DB_POOL = await asyncpg.create_pool(
                user=get_db_user(),
                password=get_db_password(),
                host=get_db_host(),
                port=int(get_db_port()),
                database=get_db_name(),
                min_size=int(get_db_pool_min()),
                max_size=int(get_db_pool_max()),
                command_timeout=int(get_db_timeout()),
                ssl=ssl,
            )
            print(f"DB pool initialized: max={DB_POOL._maxsize}")
            return DB_POOL
        except Exception as e:
            print(f"DB pool init failed (attempt {attempt + 1}): {e}")
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
        print(f"DB connection acquisition failed: {e}")
        raise

# Optional: expose pool metrics for health checks
def get_pool_status():
    if DB_POOL is None:
        return {"error": "DB pool not initialized"}

    return {
        "max_size": DB_POOL._maxsize,
        "current_size": DB_POOL._queue.qsize(),
        "in_use": DB_POOL._maxsize - DB_POOL._queue.qsize()
    }

# Test pool
async def init_test_pool():
    global _TEST_POOL
    if _TEST_POOL:
        return _TEST_POOL

    _TEST_POOL = await asyncpg.create_pool(
        user=get_db_user(),
        password=get_db_password(),
        host=get_db_host(),
        port=int(get_db_port()),
        database=get_db_name(),
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