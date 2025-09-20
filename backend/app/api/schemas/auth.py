# app/api/schemas/auth.py
from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from pydantic import BaseModel, EmailStr, validator

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def strong_password(cls, v):
        if len(v) < 8 or not any(c.isdigit() for c in v) or not any(c.isupper() for c in v):
            raise ValueError("Password must be at least 8 characters, include a number and an uppercase letter")
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: UUID
    email: EmailStr
