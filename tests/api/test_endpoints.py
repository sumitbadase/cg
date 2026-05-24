"""API endpoint tests."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_pr_requires_valid_payload() -> None:
    response = client.post("/analyze-pr", json={})
    assert response.status_code == 422


def test_analyze_pr_accepts_valid_request() -> None:
    response = client.post("/analyze-pr", json={"repository": "org/repo", "pull_request_number": 42})
    assert response.status_code == 202
    assert response.json()["request_id"]


def test_drop_graph_requires_confirm() -> None:
    response = client.delete("/drop-graph")
    assert response.status_code == 400


def test_recreate_graph_returns_success() -> None:
    response = client.post("/recreate-graph")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
