from typing import Optional, Mapping, Any
from asyncpg import Connection

async def get_user_by_id(conn: Connection, user_id: str) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow(
        "SELECT id, email, created_at FROM users WHERE id = $1",
        user_id,
    )

async def get_user_by_email(conn: Connection, email: str) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow("SELECT id, email, password_hash FROM users WHERE email=$1", email)

async def create_user(conn: Connection, email: str, password_hash: str) -> Mapping[str, Any]:
    return await conn.fetchrow(
        """
        INSERT INTO users (email, password_hash)
        VALUES ($1, $2)
        RETURNING id, email, password_hash
        """,
        email, password_hash
    )