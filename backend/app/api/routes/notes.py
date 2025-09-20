from fastapi import APIRouter, HTTPException, Query, Depends, Response
from typing import List, Optional
from uuid import UUID

from ...db import db_conn
from ...repos import notes_repo
from ...core.security import get_current_user_id 
from ..schemas.notes import NoteIn, Note, NoteUpdate

router = APIRouter()

@router.get("/", response_model=List[Note])
async def list_notes(
    user_id: UUID = Depends(get_current_user_id),
    search: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
):
    async with db_conn() as conn:
        rows = await notes_repo.list_notes_by_user(conn, user_id, search, limit=limit, offset=offset)
        return [dict(r) for r in rows]

@router.post("/", response_model=Note, status_code=201)
async def create_note(payload: NoteIn, user_id: UUID = Depends(get_current_user_id)):
    async with db_conn() as conn:
        row = await notes_repo.create_note(conn, payload.title, payload.content, user_id)
        return dict(row)

@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: int, user_id: UUID = Depends(get_current_user_id)):
    async with db_conn() as conn:
        row = await notes_repo.get_note_for_user(conn, note_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Not Found")
        return dict(row)

@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    user_id: UUID = Depends(get_current_user_id),
):
    async with db_conn() as conn:
        row = await notes_repo.update_note_for_user(
            conn, note_id, user_id, payload.title, payload.content
        )
        if not row:
            raise HTTPException(status_code=404, detail="Not Found")
        return dict(row)

@router.delete("/{note_id}")
async def delete_note(note_id: int, user_id: UUID = Depends(get_current_user_id)):
    async with db_conn() as conn:
        ok = await notes_repo.delete_note_for_user(conn, note_id, user_id)
        if not ok:
            print(f"Delete failed: note_id={note_id}, user_id={user_id}")
            raise HTTPException(status_code=404, detail="Not Found")
        return Response(status_code=204)