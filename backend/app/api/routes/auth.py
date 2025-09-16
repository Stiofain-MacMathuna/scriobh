from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from ...db import db_conn
from ...core.security import (hash_password, verify_password, create_access_token, get_current_user_id)
from ...repos import users_repo         
from ..schemas.auth import RegisterIn, LoginIn, TokenOut, MeOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(payload: RegisterIn):
    async with db_conn() as conn:
        existing = await users_repo.get_user_by_email(conn, payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(payload.password)
        user = await users_repo.create_user(conn, payload.email, hashed)
        return {"id": str(user["id"]), "email": user["email"]}
    
@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    async with db_conn() as conn:
        user = await users_repo.get_user_by_email(conn, payload.email)
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(str(user["id"]))
        return {"access_token": token}
    
@router.get("/me", response_model=MeOut)
async def me(user_id: str = Depends(get_current_user_id)):
    async with db_conn() as conn:
        user = await users_repo.get_user_by_id(conn, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return {"id": str(user["id"]), "email": user["email"]}