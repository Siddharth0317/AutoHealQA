import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "engine" in data


def test_generate_tests_api():
    payload = {
        "requirement_text": "Verify user can navigate to homepage and view banner header",
        "target_url": "https://example.com"
    }
    response = client.post("/api/v1/generate-tests", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "scenarios" in data
    assert len(data["scenarios"]) > 0


def test_history_api():
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data


def test_admin_metrics_rbac():
    # Attempt without admin role header (should fail with 403)
    response_denied = client.get("/api/v1/admin/metrics", headers={"X-User-Role": "tester"})
    assert response_denied.status_code == 403

    # Attempt with admin role header (should succeed with 200)
    response_allowed = client.get("/api/v1/admin/metrics", headers={"X-User-Role": "admin"})
    assert response_allowed.status_code == 200
    data = response_allowed.json()
    assert "total_test_generations" in data
    assert "self_healing_success_rate" in data
