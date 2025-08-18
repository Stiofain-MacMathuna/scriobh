from fastapi import FastAPI
from .notes import router as notes_router

app = FastAPI()

# health check route.
@app.get("/health")
def health():
    return {"ok": True}

app.include_router(notes_router, prefix="/notes", tags=["notes"])