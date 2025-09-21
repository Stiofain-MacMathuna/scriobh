from typing import Optional, Mapping, Any
from asyncpg import Connection

# GET USER BY ID
async def get_user_by_id(conn: Connection, user_id: str) -> Optional[Mapping[str, Any]]:
    try:
        await conn.execute("SET LOCAL statement_timeout = 10000")
        return await conn.fetchrow(
            "SELECT id, email, created_at FROM users WHERE id = $1",
            user_id,
        )
    except Exception as e:
        print(f"get_user_by_id failed: {e}")
        return None

# GET USER BY EMAIL
async def get_user_by_email(conn: Connection, email: str) -> Optional[Mapping[str, Any]]:
    try:
        await conn.execute("SET LOCAL statement_timeout = 10000")
        return await conn.fetchrow(
            "SELECT id, email, password_hash FROM users WHERE email = $1",
            email
        )
    except Exception as e:
        print(f"get_user_by_email failed: {e}")
        return None

# CREATE USER
async def create_user(conn: Connection, email: str, password_hash: str) -> Optional[Mapping[str, Any]]:
    try:
        await conn.execute("SET LOCAL statement_timeout = 10000")
        return await conn.fetchrow(
            """
            INSERT INTO users (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email, password_hash
            """,
            email, password_hash
        )
    except Exception as e:
        print(f"create_user failed: {e}")
        return None