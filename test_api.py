import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_add_mountain_pass():
    response = client.post("/submitData", json={...})
    assert response.status_code == 200

def test_get_pass_by_id():
    response = client.get("/submitData/1")
    assert response.status_code == 200