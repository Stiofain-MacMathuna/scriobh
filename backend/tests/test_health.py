import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import get_test_db_conn

@pytest.mark.asyncio
async def test_health(test_pool):   
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"ok": True}

@pytest.mark.asyncio
async def test_health_db(test_pool):
    async with test_pool.acquire() as conn:
        val = await conn.fetchval("SELECT 1;", timeout=5)
        assert val == 1
