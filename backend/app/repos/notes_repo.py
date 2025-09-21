from typing import Any, Mapping, Sequence, Optional
from asyncpg import Connection
from uuid import UUID

# LIST NOTES
async def list_notes_by_user(
    conn: Connection, user_id: UUID, search: Optional[str] = None, *, limit: int, offset: int
) -> Sequence[Mapping[str, Any]]:
    if search:
        return await conn.fetch(
            """
            SELECT id, title, content, user_id, created_at, updated_at
            FROM notes
            WHERE user_id = $1 AND (title ILIKE $2 OR content ILIKE $2)
            ORDER BY updated_at DESC
            LIMIT $3 OFFSET $4
            """,
            user_id, f"%{search}%", limit, offset
        )
    return await conn.fetch(
        """
        SELECT id, title, content, user_id, created_at, updated_at
        FROM notes
        WHERE user_id = $1
        ORDER BY updated_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id, limit, offset
    )

# GET SINGLE NOTE
async def get_note_for_user(conn: Connection, note_id: int, user_id: UUID) -> Optional[Mapping[str, Any]]:
    return await conn.fetchrow(
        """
        SELECT id, title, content, user_id, created_at, updated_at
        FROM notes 
        WHERE id = $1 AND user_id = $2
        """,
        note_id, user_id,
    )

# CREATE NOTE
async def create_note(conn: Connection, title: str, content: str, user_id: UUID) -> Mapping[str, Any]:
    return await conn.fetchrow(
        """
        INSERT INTO notes (title, content, user_id)
        VALUES ($1, $2, $3)
        RETURNING id, title, content, user_id, created_at, updated_at
        """,
        title, content, user_id
    )

# UPDATE NOTE
async def update_note_for_user(
    conn: Connection,
    note_id: int,
    user_id: UUID,
    title: Optional[str],
    content: Optional[str],
) -> Optional[Mapping[str, Any]]:
    # No explicit transaction needed for single UPDATE
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
        note_id, user_id, title, content
    )

# DELETE NOTE
async def delete_note_for_user(conn: Connection, note_id: int, user_id: UUID) -> bool:
    result = await conn.execute(
        "DELETE FROM notes WHERE id = $1 AND user_id = $2",
        note_id, user_id
    )
    return result.strip().upper().startswith("DELETE 1")