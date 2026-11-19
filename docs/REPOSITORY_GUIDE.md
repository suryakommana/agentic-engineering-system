# Repository guide

## Components

| Path | Purpose |
|---|---|
| `platform_api/` | FastAPI endpoints and agentic workflow orchestration |
| `url_shortener/` | Reference URL-shortener service |
| `tests/` | Platform and URL-shortener automated tests |
| `diagrams/` | Mermaid architecture and workflow diagrams |
| `artifacts/` | Sample requirement, task plan and design/validation notes |
| `.github/workflows/` | Continuous integration |

## Local service ports
- Agentic platform: `8000`
- URL shortener: `8001`

## Runtime data
The URL-shortener demo uses a local SQLite file at `url_shortener/shortener.db`. It is intentionally ignored by Git. Back it up before deleting local data. Production should use a managed relational database and migrations.

## Workflow lifecycle
`NEEDS_CLARIFICATION` → human clarifies requirements → workflow can be resubmitted.
`NEEDS_APPROVAL` → human reviews the generated plan/evidence → explicit approval.
`BLOCKED` / `FAILED` → inspect `errors` and `events`, fix the cause, then rerun.

## Important implementation boundary
The workflow's agent outputs and engineering tasks are deterministic placeholders. They demonstrate the orchestration contract and state transitions, not live LLM-powered source-code generation. The URL shortener is a separate runnable reference application.
