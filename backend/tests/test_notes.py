from app.main import app
from app.core.security import get_current_user_id
from tests.constants import FIXED_USER_ID

app.dependency_overrides[get_current_user_id] = lambda: FIXED_USER_ID

@pytest.mark.asyncio
async def test_list_is_empty_initially(async_test_client, cleanup_notes):
    r = await async_test_client.get("/notes/")
    assert r.status_code == 200
    assert r.json() == []

@pytest.mark.asyncio
async def test_create_and_get_by_id(async_test_client, seed_auth_user):
    r = await async_test_client.post("/notes/", json={"title": "Title1", "content": "Content1"})
    assert r.status_code == 201
    note = r.json()
    note_id = note["id"]
    assert isinstance(note_id, int)

    r = await async_test_client.get(f"/notes/{note_id}/")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Title1"
    assert body["content"] == "Content1"

@pytest.mark.asyncio
async def test_update_partial(async_test_client):
    note = (await async_test_client.post("/notes/", json={"title": "Title1", "content": "Content1"})).json()
    note_id = note["id"]

    r = await async_test_client.put(f"/notes/{note_id}/", json={"content": "Content1-update"})
    assert r.status_code == 200
    body = r.json()
    assert body["content"] == "Content1-update"
    assert body["title"] == "Title1"

@pytest.mark.asyncio
async def test_delete_then_404(async_test_client, seed_auth_user):
    note = (await async_test_client.post("/notes/", json={"title": "Title1", "content": "Content1"})).json()
    note_id = note["id"]

    r = await async_test_client.delete(f"/notes/{note_id}/")
    assert r.status_code == 204

    r = await async_test_client.get(f"/notes/{note_id}/")
    assert r.status_code == 404