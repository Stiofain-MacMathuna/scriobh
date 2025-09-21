from fastapi import APIRouter, HTTPException, Query, Depends, Response
from typing import List, Optional
from uuid import UUID

from ...db import db_conn
from ...repos import notes_repo
from ...core.security import get_current_user_id 
from ..schemas.notes import NoteIn, Note, NoteUpdate

router = APIRouter()

# LIST NOTES (READ, no transaction)
@router.get("/", response_model=List[Note])
async def list_notes(
    user_id: UUID = Depends(get_current_user_id),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
):
    try:
        async with db_conn(timeout=10) as conn:
            rows = await notes_repo.list_notes_by_user(
                conn, user_id, search, limit=limit, offset=offset
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error in list_notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notes")

# GET SINGLE NOTE (READ)
@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: int, user_id: UUID = Depends(get_current_user_id)):
    try:
        async with db_conn(timeout=10) as conn:
            row = await notes_repo.get_note_for_user(conn, note_id, user_id)
    except Exception as e:
        print(f"Unexpected DB error in get_note: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    if not row:
        raise HTTPException(status_code=404, detail="Note not found")

    return dict(row)

# CREATE NOTE
@router.post("/", response_model=Note, status_code=201)
async def create_note(payload: NoteIn, user_id: UUID = Depends(get_current_user_id)):
    try:
        async with db_conn(timeout=10) as conn:
            async with conn.transaction():
                row = await notes_repo.create_note(conn, payload.title, payload.content, user_id)
            return dict(row)
    except Exception as e:
        print(f"Error in create_note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create note")

# UPDATE NOTE (WRITE)
@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    user_id: UUID = Depends(get_current_user_id),
):
    try:
        async with db_conn(timeout=10) as conn:
            async with conn.transaction():
                row = await notes_repo.update_note_for_user(
                    conn, note_id, user_id, payload.title, payload.content
                )
            if not row:
                raise HTTPException(status_code=404, detail="Note not found")
            return dict(row)
    except Exception as e:
        print(f"Error in update_note: {e}")
        raise HTTPException(status_code=500, detail="Failed to update note")

# DELETE NOTE (WRITE)
@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: int, user_id: UUID = Depends(get_current_user_id)):
    try:
        async with db_conn(timeout=10) as conn:
            async with conn.transaction():
                success = await notes_repo.delete_note_for_user(conn, note_id, user_id)
            if not success:
                raise HTTPException(status_code=404, detail="Note not found")
            return Response(status_code=204)
    except Exception as e:
        print(f"Error in delete_note: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")
