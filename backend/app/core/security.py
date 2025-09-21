import bcrypt
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from .config import JWT_SECRET, JWT_ALG, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Synchronous bcrypt hashing
def _hash_sync(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Synchronous bcrypt verification
def _verify_sync(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# Async wrapper for hashing
async def hash_password(plain: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _hash_sync, plain)

# Async wrapper for verification
async def verify_password(plain: str, hashed: str) -> bool:
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, _verify_sync, plain, hashed)
    except Exception as e:
        print(f"Password verification failed: {e}")
        return False

# Create JWT access token
def create_access_token(sub: str, *, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

# Token payload model
class TokenData(BaseModel):
    sub: UUID

# Decode and validate JWT token
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        exp = payload.get("exp")

        if not sub:
            raise credentials_exc
        
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            print("Token expired")
            raise credentials_exc

        return UUID(str(sub))
    except JWTError as e:
        print(f"Token decode failed: {e}")
        raise credentials_exc