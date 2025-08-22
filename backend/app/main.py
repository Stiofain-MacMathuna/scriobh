from fastapi import FastAPI
from contextlib import asynccontextmanager
from .notes import router as notes_router
from .db import init_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    try:
        yield
    finally:
        await close_db_pool

app = FastAPI()

# health check route.
@app.get("/health")
async def health():
    return {"ok": True}

app.include_router(notes_router, prefix="/notes", tags=["notes"])