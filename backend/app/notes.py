from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from .db import db_conn
from .repos import notes_repo

router = APIRouter()

class NoteIn(BaseModel):
    """Schema for creating a new note."""
    title: str
    content: str


class Note(NoteIn):
    """Schema for returning a note, includes ID."""
    id: int


class NoteUpdate(BaseModel):
    """Schema for updating a note, fields are optional."""
    title: Optional[str] = None
    content: Optional[str] = None

@router.get("/", response_model=List[Note])
async def list_notes():
    """Return all notes."""
    async with db_conn() as conn:
        return await notes_repo.list_notes(conn)


@router.post("/", response_model=Note, status_code=201)
async def create_note(payload: NoteIn):
    """Create a new note with auto-incremented ID."""
    async with db_conn() as conn:
        return await notes_repo.create_note(conn, payload.title, payload.content)


@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: int):
    """Retrieve a single note by ID."""
    async with db_conn() as conn:
        note = await notes_repo.get_note(conn, note_id)
        if not note:
            raise HTTPException(status_code=404, details="Not Found")
        return note


@router.put("/{note_id}", response_model=Note)
async def update_note(note_id: int, payload: NoteUpdate):
    """Update a note with new values if provided."""
    async with db_conn() as conn:
        updated = await notes_repo.update_note(conn, note_id, payload.title, payload.content)
        if not updated:
            raise HTTPException(status_code=404, details="Not Found")


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int):
    """Delete a note by ID."""              
    async with db_conn as conn:
        ok = await notes_repo.delete_note(conn, note_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Not Found")
