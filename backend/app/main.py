from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.routes.notes import router as notes_router
from .db import DB_POOL, db_conn, init_db_pool, close_db_pool, get_pool_status
from .api.routes.auth import router as auth_router
from fastapi.responses import JSONResponse

# Lifespan shutdown / startup context manager. FastAPI instance calls this on start up and shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    try:
        yield
    finally:
        await close_db_pool()

# Create fastapi instance and assign to app variable.
app = FastAPI(lifespan=lifespan)

origins = [
    "http://13.60.60.57",
    "http://13.60.60.57:80",
    "http://localhost",
    "http://localhost:3000",
    "https://www.scriobh.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# mount the auth_router and notes_router (which contain many routes) onto the main FastAPI application.
app.include_router(auth_router) 
app.include_router(notes_router, prefix="/notes", tags=["notes"])

@app.get("/")
async def root():
    return {"message": "API is running"}

# health check route.
@app.get("/health", tags=["health"])
async def health():
    return {"ok": True}

# db health check.
@app.get("/health/db", tags=["health"])
async def health_db():
    # Fetch connection from the connection pool.
    async with db_conn() as conn:
        try:
            val = await conn.fetchval("SELECT 1;") # use await so that if no connections are available the server can still continue other operations.

            ok = (val == 1)
        except Exception:
            ok = False
    code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse({"db_ok": ok}, status_code=code)

@app.get("/health/db-pool", tags=["health"])
async def health_db_pool():
    pool_status = get_pool_status()
    return pool_status
