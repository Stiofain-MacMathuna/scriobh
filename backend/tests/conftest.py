import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from app.main import app

@pytest.fixture
async def async_client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app, raise_app_exceptions=True)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

@pytest.fixture(autouse=True)
def reset_notes_state():
    try:
        from app import notes
        if hasattr(notes, "_notes"):
            notes._notes.clear()
        if hasattr(notes, "_next_id"):
            notes._next_id = 1
    except Exception:
        pass
