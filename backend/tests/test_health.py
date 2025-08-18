from fastapi.testclient import TestClient
from app.main import app

# Declaring an instance of the test client class that is connected to the FastAPI app instance.
client = TestClient(app)

def test_health():
    r = client.get("/health") # fake request sent to the health endpoint. JSON string is now contained in the r variable.
    assert r.status_code == 200 # asserts that r's status code is 200.
    assert r.json() == {"ok": True} # asserts that the json matches.