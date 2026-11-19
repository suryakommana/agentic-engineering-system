# URL shortener requirement
Build a scalable URL shortener service with APIs, persistence, and analytics.

## Acceptance criteria
- Valid destination URL creates a unique short code.
- Custom aliases are supported and unique.
- Active short codes return HTTP 302.
- Unknown codes return HTTP 404.
- Expired codes return HTTP 410.
- Click counts are queryable.
- Invalid URLs are rejected.
- Persistence survives application restart.

## Non-functional goals
Stateless API tier, cacheable redirect path, durable storage, asynchronous analytics in production, rate limiting and observability.
