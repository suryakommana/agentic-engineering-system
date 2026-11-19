# Architecture decisions
1. Modular monolith for prototype; preserve boundaries for later service extraction.
2. PostgreSQL recommended for production; SQLite used for zero-friction local run.
3. Redis cache-aside for hot redirects; datastore remains source of truth.
4. Queue-backed analytics in production to decouple redirects from analytics latency.
5. HTTP 302 avoids sticky permanent browser caching.
6. Base62 code generation uses uniqueness enforcement; collisions are not assumed impossible.
7. Agents create candidate changes only; human owns merge and deployment.
