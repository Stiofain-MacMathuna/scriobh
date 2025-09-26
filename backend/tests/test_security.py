import pytest
import uuid
from app.core import security as sec
from jose import jwt

@pytest.mark.asyncio
async def test_hash_and_verify_password():
    password = "mypassword"
    hashed = await sec.hash_password(password)  
    assert hashed != password
    assert await sec.verify_password(password, hashed)
    assert not await sec.verify_password("wrongpassword", hashed)

@pytest.mark.asyncio
async def test_create_access_token_and_decode(test_pool):
    sub = str(uuid.uuid4())
    token = sec.create_access_token(sub, expires_minutes=1)
    decoded = jwt.decode(token, sec.get_jwt_secret(), algorithms=[sec.get_jwt_alg()])
    assert decoded["sub"] == sub
    assert "iat" in decoded
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_get_current_user_id_valid_token(test_pool):
    sub = uuid.uuid4()
    token = sec.create_access_token(str(sub))
    user_id = await sec.get_current_user_id(token=token)
    assert user_id == sub

@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token(test_pool):
    with pytest.raises(Exception) as exc:
        await sec.get_current_user_id(token="invalid.token.here")
    assert "Could not validate credentials" in str(exc.value)