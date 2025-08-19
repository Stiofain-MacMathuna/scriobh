from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

# APIRouter enables routes declared in files other than main.py to connect to the main FastAPI app declared in the main.py file.
# Bundles routes into a mini-app that is then connected to the main FastAPI app.
router = APIRouter()

# Declares a class that inherits from pydantic's BaseModel class. When json is received from the frontend, pydantic will parse this json data into 
# a python dict object, compare this dict to the class attributes of the NoteIn class, and if correct create a NoteIn object.
class NoteIn(BaseModel):
	title: str
	content: str

# Inherits all attributes from the NoteIn class which in turns inherits from the BaseModel class.
class Note(NoteIn):
	id: int

# Inherits from BaseModel class (pydantic)
class NoteUpdate(BaseModel):		
	title: Optional[str] = None # title can be either a string or None. 
	conent: Optional [str] = None

# notes stored in memory for the time being until 
_notes: List[Note] = []
_next_id = 1

# "/" is the root of the router which is attached to the prefix /notes/
@router.get("/", response_model=List[Note]) # The response must be a List of note objects.
def list_notes():
	return _notes

@router.post("/", response_model=Note, status_code=201) # response must be a single note.
def create_note(payload:NoteIn):
	global _next_id # global variables as _next_id is declared outside of this functions scope.
	note = Note(id=_next_id, **payload.model_dump()) # payload.model_dump converts the payload from a NoteIn object instance back into a dict. 
	_notes.append(note) # Adds the note instance to the test list.
	_next_id += 1 # increments id counter.
	return note

@router.get("/{note_id}", response_model=Note) # response body must be a single note.
def get_note(note_id: int):
	for n in _notes:
		if  n.id  == note_id:
			return n
	raise HTTPException(status_code=404, detail="Not Found")

@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate): # parse json to dict, validate against NoteUpdate, and if correct create NoteUpdate instance.
	for i, n in enumerate (_notes): # Use enumerate to get the index in  the list and the note object itself. 
		if n.id == note_id: # if the id value of the note object in question is equal to the incoming note_id then proceed.

			# n is the existing note object. model_copy pydantic model that creates a copy of the note but with the given fields updated.
			# items() method gives us the key value pair in the dict. 
			# the dict comprehenstion then creates a new dictionary that removes any null values and then merges into the original note.
			updated = n.model_copy(update={key: value for key, value in payload.model_dump().items() if value is not None})
			_notes[i] = updated # replace the original note with the newly updated data.
			return updated
	raise HTTPException(status_code=404, detail="Not Found")

@router.delete ("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
	for i, n in enumerate(_notes):
		if n.id == note_id:
			del _notes[i]
			return
	raise HTTPException(status_code=404, detail="Not Found")
