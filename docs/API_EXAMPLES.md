# API examples

## Agentic platform

Start:
```bash
uvicorn platform_api.main:app --reload --port 8000
```

Create workflow:
```bash
curl -X POST http://127.0.0.1:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{"requirement":"Build a scalable URL shortener service with APIs, persistence, and analytics.","scenario":"greenfield","inject_failure_once":true}'
```

Read workflow:
```bash
curl http://127.0.0.1:8000/workflows/<workflow_id>
```

Approve after review:
```bash
curl -X POST http://127.0.0.1:8000/workflows/<workflow_id>/approve
```

## URL shortener

Start:
```bash
uvicorn url_shortener.main:app --reload --port 8001
```

Create:
```bash
curl -X POST http://127.0.0.1:8001/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com/docs","custom_alias":"docs-home"}'
```

Redirect: `GET http://127.0.0.1:8001/docs-home`

Analytics: `GET http://127.0.0.1:8001/api/v1/urls/docs-home/analytics`
