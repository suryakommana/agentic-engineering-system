"""FastAPI entry point for the agentic engineering platform demo.

Workflow records are in-memory for this prototype. Use a durable database and
checkpoint store before deploying multiple API replicas.
"""
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from .models import WorkflowRequest
from .orchestrator import Orchestrator

app = FastAPI(
    title="Agentic Software Engineering Platform",
    version="1.1.0",
    description="Requirement-to-engineering workflow with DAG execution and approval gates.",
)
orchestrator = Orchestrator()
workflows = {}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/workflows")
async def create_workflow(request: WorkflowRequest):
    result = await orchestrator.execute(request)
    workflows[result["workflow_id"]] = result
    return result

@app.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    result = workflows.get(workflow_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result

@app.post("/workflows/{workflow_id}/approve")
def approve_workflow(workflow_id: str):
    result = workflows.get(workflow_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if result["status"] != "NEEDS_APPROVAL":
        raise HTTPException(status_code=409, detail="Workflow is not awaiting approval")
    result["status"] = "APPROVED"
    result["summary"]["human_approval"] = "APPROVED"
    result["events"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": "human_approval", "status": "APPROVED",
    })
    return {"workflow_id": workflow_id, "status": "APPROVED"}
