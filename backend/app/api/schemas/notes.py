from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class NoteIn(BaseModel):
    title: str
    content: str

class Note(BaseModel):
    id: int
    user_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
