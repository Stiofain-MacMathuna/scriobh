# app/api/schemas/auth.py
from pydantic import BaseModel, EmailStr
from uuid import UUID

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: UUID
    email: EmailStr
