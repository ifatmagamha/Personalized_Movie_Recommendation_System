import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_recommend_endpoint():
    payload = {
        "user_id": 1,
        "query": "",
        "k": 5,
        "mode": "baseline",
        "candidate_pool": 2000
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    assert "recommendations" in response.json()
    assert len(response.json()["recommendations"]) <= 5

def test_feedback_endpoint():
    payload = {
        "user_id": 1,
        "movieId": 123,
        "action": "like",
        "context": {"screen": "results"}
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"