from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class NoteIn(BaseModel):
	title: str
	content: str

class Note(NoteIn):
	id: int

_notes: List[Note] = []
_next_id = 1

@router.get("/", response_model=List[Note])
def list_notes():
	return _notes

@router.post("/", response_model=Note, status_code=201)
def create_note(payload:NoteIn):
	global _next_id
	note = Note(id=_next_id, **payload.model_dump())
	_notes.append(note)
	_next_id += 1
	return note

@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int):
	for n in _notes:
		if  n.id  == note_id:
			return n
	raise HTTPException(status_code=404, detail="Not Found")
