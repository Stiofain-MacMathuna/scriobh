from typing import Any, Mapping, Sequence, Optional
from asyncpg import Connection
from uuid import UUID

async def list_notes_by_user(conn: Connection, user_id: UUID, *, limit:int, offset:int) -> Sequence[Mapping[str, Any]]:                                             
    return await conn.fetch(
        """SELECT id, title, content, user_id, created_at, updated_at
        FROM notes
        WHERE user_id = $1
        ORDER BY updated_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id, limit, offset
    )

async def get_note_for_user(conn: Connection, note_id: int, user_id: UUID) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow(
        """SELECT id, title, content, user_id, created_at, updated_at
        FROM notes 
        WHERE id = $1 AND user_id = $2
        """,
        note_id, user_id,
)

async def update_note_for_user(
    conn: Connection,
    note_id: int,
    user_id: UUID,
    title: Optional[str],
    content: Optional[str],
) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow(
        """
        UPDATE notes
        SET
          title = COALESCE($3, title),
          content = COALESCE($4, content),
          updated_at = now()
        WHERE id = $1 AND user_id = $2
        RETURNING id, title, content, user_id, created_at, updated_at
        """,
        note_id, user_id, title, content,
    )

async def delete_note_for_user(conn: Connection, note_id: int, user_id: UUID) -> bool:
    result = await conn.execute(
        "DELETE FROM notes WHERE id = $1 AND user_id = $2",
        note_id, user_id,
    )
    return result.upper().startswith("DELETE 1")


async def list_notes(conn: Connection) -> Sequence[Mapping[str, Any]]:
    return await conn.fetch(
        "SELECT id, title, content, user_id FROM notes ORDER BY id ASC"
    )

async def create_note(conn: Connection, title: str, content: str, user_id: UUID) -> Mapping[str, Any]:
    return await conn.fetchrow(
        """
        INSERT INTO notes (title, content, user_id)
        VALUES ($1, $2, $3)
        RETURNING id, title, content, user_id, created_at, updated_at
        """,
        title, content, user_id
    )

async def get_note(conn: Connection, note_id: int) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow(
        "SELECT id, title, content, user_id FROM notes WHERE id = $1",
        note_id,
    )

async def update_note(
    conn: Connection,
    note_id: int,
    title: Optional[str],
    content: Optional[str],
) -> Optional[Mapping[str, Any]]:
        return await conn.fetchrow(
        """
        UPDATE notes
        SET
          title = COALESCE($2, title),
          content = COALESCE($3, content),
          updated_at = now()
        WHERE id = $1
        RETURNING id, title, content, user_id, created_at, updated_at
        """,
        note_id, title, content
    )

async def delete_note(conn: Connection, note_id: int) -> bool:
    result = await conn.execute("DELETE FROM notes WHERE id = $1", note_id)
    return result.upper().startswith("DELETE 1")
