from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

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


# Temporary in-memory store until DB integration
_notes: List[Note] = []
_next_id = 1


@router.get("/", response_model=List[Note])
def list_notes():
    """Return all notes."""
    return _notes


@router.post("/", response_model=Note, status_code=201)
def create_note(payload: NoteIn):
    """Create a new note with auto-incremented ID."""
    global _next_id
    note = Note(id=_next_id, **payload.model_dump())
    _notes.append(note)
    _next_id += 1
    return note


@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int):
    """Retrieve a single note by ID."""
    for n in _notes:
        if n.id == note_id:
            return n
    raise HTTPException(status_code=404, detail="Not Found")


@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate):
    """Update a note with new values if provided."""
    for i, n in enumerate(_notes):
        if n.id == note_id:
            updated = n.model_copy(
                update={k: v for k, v in payload.model_dump().items() if v is not None}
            )
            _notes[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Not Found")


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    """Delete a note by ID."""
    for i, n in enumerate(_notes):
        if n.id == note_id:
            del _notes[i]
            return
    raise HTTPException(status_code=404, detail="Not Found")
