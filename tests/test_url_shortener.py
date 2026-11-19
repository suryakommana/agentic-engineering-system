from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from url_shortener.main import app
from url_shortener import db

def setup_function():
    with db.connect() as conn:
        conn.execute("DROP TABLE IF EXISTS urls")
    db.initialize()

client = TestClient(app)

def test_create_and_redirect():
    response = client.post("/api/v1/urls", json={"original_url":"https://example.com/path"})
    assert response.status_code == 201
    code = response.json()["short_code"]
    redirected = client.get(f"/{code}", follow_redirects=False)
    assert redirected.status_code == 302
    assert redirected.headers["location"] == "https://example.com/path"

def test_duplicate_custom_alias():
    payload = {"original_url":"https://example.com","custom_alias":"my-link"}
    assert client.post("/api/v1/urls", json=payload).status_code == 201
    assert client.post("/api/v1/urls", json=payload).status_code == 409

def test_unknown_code():
    assert client.get("/not-found", follow_redirects=False).status_code == 404

def test_analytics_count():
    response = client.post("/api/v1/urls", json={"original_url":"https://example.com"})
    code = response.json()["short_code"]
    client.get(f"/{code}", follow_redirects=False)
    metrics = client.get(f"/api/v1/urls/{code}/analytics")
    assert metrics.status_code == 200
    assert metrics.json()["click_count"] == 1

def test_expired_url_returns_410():
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    created = client.post("/api/v1/urls", json={
        "original_url":"https://example.com/expired",
        "custom_alias":"expired-link",
        "expires_at":expired
    })
    assert created.status_code == 201
    assert client.get("/expired-link", follow_redirects=False).status_code == 410

def test_naive_expiry_is_treated_as_utc():
    naive_past = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None).isoformat()
    created = client.post("/api/v1/urls", json={
        "original_url":"https://example.com/naive",
        "custom_alias":"naive-link",
        "expires_at":naive_past
    })
    assert created.status_code == 201
    assert client.get("/naive-link", follow_redirects=False).status_code == 410

def test_invalid_url_rejected():
    response = client.post("/api/v1/urls", json={"original_url":"not-a-url"})
    assert response.status_code == 422
