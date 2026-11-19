# Validation strategy
- Compile/import check, Ruff, Pytest, API contract validation, Bandit and pip-audit in CI.
- Integration tests against real PostgreSQL/Redis in production-like CI.
- URL tests: create 201, invalid 422, duplicate alias 409, redirect 302, unknown 404, expired 410, analytics count, concurrent alias collision.
- Retry transient failures with bounded exponential backoff. Do not auto-retry security/policy violations.
- Block downstream tasks when dependencies fail. Escalate after retry budget exhaustion.
- Passing tests are evidence, not proof; add load, chaos, threat-model, privacy and restore testing before production.
