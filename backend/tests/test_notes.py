# tests/test_notes_async.py
import pytest

pytestmark = pytest.mark.asyncio

pytestmark = pytest.mark.skip(reason="Skipping DB-dependent tests until database is configured")

@pytest.mark.asyncio
async def test_list_is_empty_initially(async_client):
    r = await async_client.get("/notes/")
    assert r.status_code == 200
    assert r.json() == []

@pytest.mark.asyncio
async def test_create_and_get_by_id(async_client):
    r = await async_client.post("/notes/", json={"title": "Title1", "content": "Content1"})
    assert r.status_code == 201
    note = r.json()
    assert note["id"] == 1

    r = await async_client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Title1"

@pytest.mark.asyncio
async def test_update_partial(async_client):
    note = (await async_client.post("/notes/", json={"title": "Title1", "content": "Content1"})).json()
    r = await async_client.put(f"/notes/{note['id']}", json={"content": "Content1-update"})
    assert r.status_code == 200
    assert r.json()["content"] == "Content1-update"
    assert r.json()["title"] == "Title1"

@pytest.mark.asyncio
async def test_delete_then_404(async_client):
    note = (await async_client.post("/notes/", json={"title": "Title1", "content": "Content1"})).json()
    r = await async_client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204

    r = await async_client.get(f"/notes/{note['id']}")
    assert r.status_code == 404
