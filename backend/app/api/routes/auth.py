from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from ...db import db_conn
from ...core.security import (hash_password, verify_password, create_access_token, get_current_user_id)
from ...repos import users_repo, notes_repo  
from ..schemas.auth import RegisterIn, LoginIn, TokenOut, MeOut

router = APIRouter(prefix="/auth", tags=["auth"])

# The content of the welcome note.
WELCOME_NOTE_CONTENT = """# Welcome to scriobh!

This is a **Markdown-enabled notes app**, built with computer science students in mind. It’s designed to make it easy to take well-structured notes during lectures, tutorials, and coding sessions.

In the bottom-left  corner of the app, you’ll find three important buttons:

1. New Note – Create a fresh note instantly.

2. Toggle Markdown Mode – Switch between plain text and Markdown preview mode to format your notes.

3. Logout – Securely log out of your account when you’re done.

## Markdown Features

* **Headings**: Use `#` for different heading sizes.
* **Bold**: Wrap text in `**double asterisks**`.
* **Italics**: Use `*single asterisks*`.
* **Lists**: Start a line with `*` or `-`.

---

### Code Blocks

You can display code by wrapping it in backticks.

`console.log("Hello, World!");`

You can also create multi-line code blocks like this:

```javascript
function sayHello() {
  console.log("Welcome to scriobh!");
}
sayHello();"""

@router.post("/register", status_code=201)
async def register(payload: RegisterIn):
    async with db_conn() as conn:
        existing = await users_repo.get_user_by_email(conn, payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(payload.password)
        user = await users_repo.create_user(conn, payload.email, hashed)

        # After creating the user, create the welcome note
        note = await notes_repo.create_note(
        conn, 
        title="Welcome!", 
        content=WELCOME_NOTE_CONTENT, 
        user_id=user["id"]
    )
        print("DEBUG - Welcome note created:", note)

        token = create_access_token(str(user["id"]))
        return {"access_token": token, "token_type": "bearer"}
    
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