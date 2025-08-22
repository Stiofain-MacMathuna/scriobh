from typing import List, Optional, Any, Mapping
from asyncpg import Connection

async def list_notes(conn: Connection) -> List[Mapping[str, Any]]:
    rows = await conn.fetch(
        "SELECT id, title, content FROM notes Order by id ASC"
    )
    return [dict(r) for r in rows]

async def create_note(conn: Connection, title: str, content: str) -> Mapping[str, Any]:
    row = await conn.fetchrow(
        """
        INSERT INTO notes (title, content)
        VALUES ($1, $2)
        RETURNING id, title, content
        """,
        title, content
    )
    return dict(row)

async def get_note(conn: Connection, note_id: int) -> Optional[Mapping[str, Any]]:
    row = await conn.fetchrow(
        "SELECT id, title, content FROM notes WHERE id = $1",
        note_id
    )
    return dict(row) if row else None

async def update_note(conn:Connection, note_id: int, title: Optional[str], content: Optional[str]) -> Optional[Mapping[str,Any]]:
    sets = []
    args = []
    if title is not None:
        sets.append("title = ${}".format(len(args)+1)); args.append(title)
    if content is not None:
        sets.append("content = ${}".format(len(args)+1)); args.append(content)
    if not sets:
        return await get_note(conn, note_id)
    
    args.append(note_id)
    sql = f"""
        UPDATE notes SET {", ".join(sets)}, updated_at = now()
        WHERE id = ${len(args)} RETURNING id, title, content
    """
    row = await conn.fetchrow(sql, *args)
    return dict(row) if row else None

async def delete_note(conn: Connection, note_id: int) -> bool:
    res = await conn.execute("DELETE FROM notes where id = $1", note_id)
    return res.endswith("1")