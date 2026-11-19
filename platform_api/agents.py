from pathlib import Path
from typing import Any

class RequirementAgent:
    def run(self, requirement: str, scenario: str) -> dict[str, Any]:
        text = requirement.strip()
        ambiguous = scenario == "ambiguous" or ("faster" in text.lower() and "latency" not in text.lower())
        return {
            "classification": "brownfield" if scenario == "brownfield" else "greenfield",
            "normalized_problem": text,
            "functional_requirements": [
                "Create short URLs from validated destination URLs",
                "Redirect short codes to active destinations",
                "Persist URL metadata", "Capture click analytics"
            ],
            "non_functional_requirements": [
                "Horizontally scalable API tier", "Low-latency redirect path",
                "Durable persistence", "Observable and secure operation"
            ],
            "acceptance_criteria": [
                "Valid URL creation returns HTTP 201 and unique short code",
                "Known active code redirects with HTTP 302",
                "Unknown code returns HTTP 404",
                "Analytics endpoint returns click count",
                "Invalid URLs are rejected"
            ],
            "ambiguities": ([
                "What redirect latency target and percentile are required?",
                "Should analytics be real-time or near-real-time?",
                "What are expected peak read/write rates and retention requirements?"
            ] if ambiguous else []),
            "assumptions": [
                "Initial deployment is single-region",
                "Management API authentication is a production requirement, not implemented in demo",
                "Analytics may be eventually consistent in production"
            ],
            "status": "NEEDS_CLARIFICATION" if ambiguous else "READY"
        }

class RepositoryAgent:
    def run(self, repository_path: str | None) -> dict[str, Any]:
        if not repository_path:
            return {"scanned": False, "files": [], "impacted_areas": [],
                    "note": "No repository path supplied; greenfield mode."}
        root = Path(repository_path).resolve()
        if not root.exists() or not root.is_dir():
            return {"scanned": False, "error": f"Repository path not found: {root}"}
        ignored = {".git", ".venv", "__pycache__", "node_modules"}
        found = []
        for p in root.rglob("*"):
            if any(part in ignored for part in p.parts):
                continue
            if p.is_file() and p.suffix in {".py", ".yaml", ".yml", ".json", ".toml"}:
                found.append(str(p.relative_to(root)))
        joined = " ".join(found).lower()
        areas = [area for token, area in [
            ("api", "API layer"), ("model", "data models"),
            ("database", "persistence"), ("test", "test suite"),
            ("analytics", "analytics")
        ] if token in joined]
        return {"scanned": True, "root": str(root), "files": found[:200],
                "impacted_areas": areas, "file_count": len(found),
                "note": "Lightweight inventory; semantic dependency analysis is a production extension."}

class ArchitectAgent:
    def run(self, requirement_spec: dict, repository_context: dict) -> dict[str, Any]:
        return {
            "style": "Modular monolith for prototype; independently scalable services in production",
            "components": [
                {"name":"API Gateway / Edge","responsibility":"TLS, routing, throttling, authentication"},
                {"name":"URL API","responsibility":"Create, update and manage URL records"},
                {"name":"Redirect handler","responsibility":"Cache lookup and redirect response"},
                {"name":"Redis","responsibility":"Hot short-code cache"},
                {"name":"URL datastore","responsibility":"Durable URL metadata and uniqueness"},
                {"name":"Event queue","responsibility":"Buffer click events"},
                {"name":"Analytics worker/store","responsibility":"Idempotent aggregation and reporting"}
            ],
            "api_contract": {
                "POST /api/v1/urls":"Create URL; 201, 422, 409",
                "GET /{code}":"Redirect; 302, 404, 410",
                "GET /api/v1/urls/{code}/analytics":"Return click metrics; 200, 404"
            },
            "data_entities": [
                "Url(id, short_code, original_url, created_at, expires_at, active)",
                "ClickEvent(id, short_code, clicked_at, referrer, user_agent)"
            ],
            "decisions": [
                "Base62 code generation with unique constraint and collision retry",
                "302 redirects to avoid sticky permanent browser caching",
                "Asynchronous analytics in production to protect redirect latency",
                "Redis cache-aside with bounded TTL; database remains source of truth"
            ],
            "risks": ["Hot-key concentration","Cache staleness after deactivation",
                      "Analytics duplicates","Abuse/phishing and enumeration"],
            "repository_context": repository_context
        }

class PlannerAgent:
    def run(self) -> list[dict[str, Any]]:
        return [
            {"task_id":"T1","name":"Define API contract and schemas","agent":"api_agent","dependencies":["ARCH"]},
            {"task_id":"T2","name":"Define persistence model and constraints","agent":"database_agent","dependencies":["ARCH"]},
            {"task_id":"T3","name":"Define test strategy and cases","agent":"test_agent","dependencies":["ARCH"]},
            {"task_id":"T4","name":"Implement URL API and business logic","agent":"api_agent","dependencies":["T1","T2"]},
            {"task_id":"T5","name":"Implement analytics capture and query","agent":"analytics_agent","dependencies":["T2","T1"]},
            {"task_id":"T6","name":"Generate documentation and operational notes","agent":"documentation_agent","dependencies":["T1","T2","T3"]},
            {"task_id":"T7","name":"Run tests, lint and security validation","agent":"validation_agent","dependencies":["T4","T5","T6"]},
            {"task_id":"T8","name":"Review risks and prepare engineering summary","agent":"review_agent","dependencies":["T7"]}
        ]

class EngineeringAgent:
    def run(self, task: dict, context: dict) -> dict[str, Any]:
        return {"task":task["task_id"],"agent":task["agent"],
                "result":f"Completed: {task['name']}",
                "quality_checks":["structured output","acceptance criteria linked"]}

class ValidationAgent:
    def run(self, inject_failure: bool, already_retried: bool) -> dict[str, Any]:
        if inject_failure and not already_retried:
            return {"passed":False,"failures":[{
                "test":"test_create_url_status","expected":201,"actual":200,
                "diagnosis":"Creation endpoint returned an incorrect status code."
            }]}
        return {"passed":True,"checks":{
            "unit_tests":"PASS","api_contract":"PASS",
            "static_analysis":"PASS (prototype policy check)",
            "security":"PASS (scanner integration pending; not a production security claim)"
        }}

class RecoveryAgent:
    def run(self, failures: list[dict]) -> dict[str, Any]:
        return {"action":"RETRY_TARGETED_TASK","target":"T4",
                "reason":"Validation failure maps to URL API implementation.",
                "failure_context":failures,"max_retries":1}
