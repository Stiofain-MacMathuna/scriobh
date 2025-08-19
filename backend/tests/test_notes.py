from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_notes_state():
    # runs before each test
    from app import notes
    notes._notes.clear()
    notes._next_id = 1

def test_list_is_empty_initially():
    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []

def test_create_and_get_by_id():
    r = client.post("/notes", json={"title": "Title1", "content": "Content1"})
    assert r.status_code == 201
    note = r.json()
    assert note["id"] == 1

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Title1"

def test_update_partial():
    note = client.post("/notes/", json={"title": "Title1", "content": "Content1"}).json()
    r = client.put(f"/notes/{note['id']}", json={"content": "Content1-update"})
    assert r.status_code == 200
    assert r.json()["content"] == "Content1-update"
    assert r.json()["title"] == "Title1"

def test_delete_then_404():
    note = client.post("/notes/", json={"title": "Title1", "content": "Content1"}).json()
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 404
