import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.json["status"] == "OK"

def test_predict(client):
    rv = client.post("/predict", json={"query": "SELECT * FROM users"})
    assert rv.status_code == 200
    assert "is_sqli" in rv.json
