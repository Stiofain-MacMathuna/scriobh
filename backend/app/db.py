import os
import asyncpg
from contextlib import asynccontextmanager

DB_POOL = None

async def init_db_pool():
    global DB_POOL
    if DB_POOL:
        return DB_POOL
    
    #SSL for RDS
    ssl_mode = os.getenv("DB_SSL_MODE", "disable")
    ssl = False if ssl_mode == "disable" else "require"

    DB_POOL = await asyncpg.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        min_size=int(os.getenv("DB_POOL_MIN", "1")),
        max_size=int(os.getenv("DB_POOL_MAX", "10")),
        command_timeout=int(os.getenv("DB_TIMEOUT", "10")),
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
    """
    Usage:
        async with db_conn() as conn:
        await conn.execute(...)
    """
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn