import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_export_code_api():
    payload = {
        "test_suite": {
            "id": "suite-api-01",
            "title": "API Export Test",
            "summary": "Testing export API",
            "target_url": "https://example.com",
            "prerequisites": [],
            "scenarios": [
                {
                    "id": "SC-01",
                    "title": "Main Flow",
                    "gherkin_text": "Given On page",
                    "given": ["On page"],
                    "when": ["Click"],
                    "then": ["Assert"],
                    "test_steps": [
                        {
                            "step_number": 1,
                            "action": "navigate",
                            "target_description": "Navigate",
                            "selector_hint": None,
                            "input_value": "https://example.com",
                            "expected_outcome": "Loaded"
                        }
                    ],
                    "edge_cases": []
                }
            ],
            "metadata": {}
        },
        "export_format": "python"
    }

    res = client.post("/api/v1/export-code", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["filename"] == "suite-api-01.py"
    assert "exported_code" in data
    assert "def test_sc_01_main_flow" in data["exported_code"]


def test_jira_webhook_api():
    jira_payload = {
        "issue_key": "QA-777",
        "summary": "Verify checkout payment button",
        "description": "User clicks payment button and sees confirmation toast",
        "target_url": "https://example.com"
    }

    res = client.post("/api/v1/webhooks/jira", json=jira_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["jira_issue"] == "QA-777"
    assert "suite_id" in data
    assert "run_id" in data
