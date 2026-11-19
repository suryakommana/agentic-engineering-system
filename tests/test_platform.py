from fastapi.testclient import TestClient
from platform_api.main import app

client = TestClient(app)

def test_greenfield_workflow_reaches_approval_gate():
    response = client.post("/workflows", json={
        "requirement":"Build a scalable URL shortener service with APIs, persistence, and analytics.",
        "scenario":"greenfield"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NEEDS_APPROVAL"
    assert body["summary"]["tasks_completed"] == 8
    assert any(e["step"] == "parallel_batch" for e in body["events"])

def test_ambiguous_requirement_pauses():
    response = client.post("/workflows", json={
        "requirement":"Make the URL shortener faster and improve analytics.",
        "scenario":"ambiguous"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "NEEDS_CLARIFICATION"

def test_validation_failure_triggers_bounded_recovery():
    response = client.post("/workflows", json={
        "requirement":"Build a scalable URL shortener service with APIs, persistence, and analytics.",
        "scenario":"greenfield",
        "inject_failure_once":True
    })
    body = response.json()
    assert body["status"] == "NEEDS_APPROVAL"
    assert body["recovery"]["max_retries"] == 1
    assert any(e["step"] == "validation_retry" for e in body["events"])

def test_human_approval_gate():
    response = client.post("/workflows", json={
        "requirement":"Build a scalable URL shortener service with APIs, persistence, and analytics.",
        "scenario":"greenfield"
    })
    workflow_id = response.json()["workflow_id"]
    approved = client.post(f"/workflows/{workflow_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

def test_unknown_workflow_is_404():
    assert client.get("/workflows/not-a-real-id").status_code == 404
