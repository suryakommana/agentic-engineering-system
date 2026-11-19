"""Dependency-aware orchestration with bounded recovery and explicit failure states."""
import asyncio
import uuid
from datetime import datetime, timezone
from .agents import (
    RequirementAgent, RepositoryAgent, ArchitectAgent, PlannerAgent,
    EngineeringAgent, ValidationAgent, RecoveryAgent,
)

TASK_TIMEOUT_SECONDS = 60

class Orchestrator:
    def __init__(self):
        self.requirements = RequirementAgent()
        self.repository = RepositoryAgent()
        self.architect = ArchitectAgent()
        self.planner = PlannerAgent()
        self.engineer = EngineeringAgent()
        self.validator = ValidationAgent()
        self.recovery = RecoveryAgent()

    async def execute(self, request):
        workflow_id = str(uuid.uuid4())
        events, errors = [], []

        def event(name, status, details=None):
            events.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": name, "status": status, "details": details or {},
            })

        try:
            req = self.requirements.run(request.requirement, request.scenario)
            event("requirement_analysis", req["status"], {"ambiguities": req["ambiguities"]})
            if req["status"] == "NEEDS_CLARIFICATION":
                return {
                    "workflow_id": workflow_id, "status": "NEEDS_CLARIFICATION",
                    "requirement_spec": req, "events": events,
                    "summary": {"message": "Paused; human clarification required."},
                }

            repo = self.repository.run(request.repository_path)
            if repo.get("error"):
                raise ValueError(repo["error"])
            event("repository_analysis", "COMPLETED", {"file_count": repo.get("file_count", 0)})
            architecture = self.architect.run(req, repo)
            event("architecture", "COMPLETED")
            tasks = self.planner.run()
            event("task_planning", "COMPLETED", {"task_count": len(tasks)})

            completed = {"ARCH"}
            outputs, pending = {}, {t["task_id"]: t for t in tasks}
            while pending:
                ready = [
                    task for task in pending.values()
                    if set(task["dependencies"]).issubset(completed)
                ]
                if not ready:
                    unresolved = {key: value["dependencies"] for key, value in pending.items()}
                    raise RuntimeError(f"DAG deadlock or failed dependency: {unresolved}")

                event("parallel_batch", "RUNNING", {"tasks": [t["task_id"] for t in ready]})
                results = await asyncio.gather(*[
                    asyncio.wait_for(
                        asyncio.to_thread(self.engineer.run, task, {"architecture": architecture}),
                        timeout=TASK_TIMEOUT_SECONDS,
                    )
                    for task in ready
                ], return_exceptions=True)

                batch_failed = False
                for task, result in zip(ready, results):
                    task_id = task["task_id"]
                    if isinstance(result, BaseException):
                        batch_failed = True
                        error = {
                            "task_id": task_id,
                            "type": type(result).__name__,
                            "message": str(result)[:1000],
                        }
                        errors.append(error)
                        task["status"] = "FAILED"
                        event(task_id, "FAILED", error)
                    else:
                        outputs[task_id] = result
                        completed.add(task_id)
                        task["status"] = "COMPLETED"
                        event(task_id, "COMPLETED", {"agent": task["agent"]})
                    pending.pop(task_id, None)

                if batch_failed:
                    for blocked in pending.values():
                        blocked["status"] = "BLOCKED"
                        event(blocked["task_id"], "BLOCKED", {"reason": "Upstream task failed"})
                    return {
                        "workflow_id": workflow_id, "status": "BLOCKED",
                        "requirement_spec": req, "repository_analysis": repo,
                        "architecture": architecture, "tasks": tasks,
                        "task_outputs": outputs, "errors": errors, "events": events,
                        "summary": {"message": "Execution stopped after task failure.",
                                    "human_approval": "NOT_ELIGIBLE"},
                    }

            validation = self.validator.run(request.inject_failure_once, False)
            event("validation", "PASSED" if validation["passed"] else "FAILED", validation)
            recovery_result = None
            if not validation["passed"]:
                recovery_result = self.recovery.run(validation["failures"])
                event("recovery", "RETRYING", recovery_result)
                validation = self.validator.run(request.inject_failure_once, True)
                event("validation_retry", "PASSED" if validation["passed"] else "FAILED", validation)

            status = "NEEDS_APPROVAL" if validation["passed"] else "BLOCKED"
            event("human_approval_gate", status)
            return {
                "workflow_id": workflow_id, "status": status,
                "requirement_spec": req, "repository_analysis": repo,
                "architecture": architecture, "tasks": tasks,
                "task_outputs": outputs, "validation": validation,
                "recovery": recovery_result, "errors": errors, "events": events,
                "summary": {
                    "scenario": request.scenario, "tasks_total": len(tasks),
                    "tasks_completed": len(completed) - 1,
                    "validation": "PASS" if validation["passed"] else "FAIL",
                    "human_approval": "PENDING" if validation["passed"] else "REQUIRED",
                    "generated_artifact_groups": [
                        "requirements", "architecture", "api_contract", "task_plan",
                        "implementation_plan", "tests", "documentation", "validation_report",
                    ],
                },
            }
        except Exception as exc:
            # Return a safe, auditable failure instead of an unhandled server exception.
            error_id = str(uuid.uuid4())
            errors.append({
                "error_id": error_id, "type": type(exc).__name__,
                "message": str(exc)[:1000],
            })
            event("workflow", "FAILED", {"error_id": error_id})
            return {
                "workflow_id": workflow_id, "status": "FAILED",
                "errors": errors, "events": events,
                "summary": {
                    "message": "Workflow failed safely. Inspect error details and retry after remediation.",
                    "human_approval": "NOT_ELIGIBLE",
                },
            }
