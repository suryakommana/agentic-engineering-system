"""Business logic for URL creation, redirects and click counters."""
import secrets
import sqlite3
import string
from datetime import datetime, timezone
from fastapi import HTTPException
from .db import connect

ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
MAX_CODE_ATTEMPTS = 8

def generate_code(length: int = 7) -> str:
    """Generate a cryptographically random Base62 short code."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def _utc(value: datetime) -> datetime:
    """Normalize aware or naive datetimes to UTC (naive values are treated as UTC)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

def create_url(original_url: str, custom_alias: str | None, expires_at):
    now = datetime.now(timezone.utc).isoformat()
    expiry = _utc(expires_at).isoformat() if expires_at else None
    try:
        with connect() as db:
            if custom_alias:
                try:
                    db.execute(
                        "INSERT INTO urls(short_code,original_url,created_at,expires_at) VALUES(?,?,?,?)",
                        (custom_alias, original_url, now, expiry),
                    )
                except sqlite3.IntegrityError as exc:
                    raise HTTPException(status_code=409, detail="Alias already exists") from exc
                code = custom_alias
            else:
                code = None
                for _ in range(MAX_CODE_ATTEMPTS):
                    candidate = generate_code()
                    try:
                        db.execute(
                            "INSERT INTO urls(short_code,original_url,created_at,expires_at) VALUES(?,?,?,?)",
                            (candidate, original_url, now, expiry),
                        )
                        code = candidate
                        break
                    except sqlite3.IntegrityError:
                        # A collision is expected to be rare; retry only uniqueness failures.
                        continue
                if code is None:
                    raise HTTPException(status_code=503, detail="Unable to allocate a unique short code")
            row = db.execute("SELECT * FROM urls WHERE short_code=?", (code,)).fetchone()
            if row is None:
                raise HTTPException(status_code=500, detail="URL record was not persisted")
            return dict(row)
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="Persistence service temporarily unavailable") from exc

def get_url(code: str):
    try:
        with connect() as db:
            row = db.execute(
                "SELECT * FROM urls WHERE short_code=? AND active=1", (code,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Short URL not found")
            if row["expires_at"]:
                expiry = _utc(datetime.fromisoformat(row["expires_at"]))
                if expiry <= datetime.now(timezone.utc):
                    raise HTTPException(status_code=410, detail="Short URL expired")
            # Atomic increment avoids a read-modify-write race between requests.
            db.execute("UPDATE urls SET click_count=click_count+1 WHERE short_code=?", (code,))
            return dict(row)
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="Persistence service temporarily unavailable") from exc

def analytics(code: str):
    try:
        with connect() as db:
            row = db.execute(
                "SELECT short_code,click_count FROM urls WHERE short_code=?", (code,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Short URL not found")
            return dict(row)
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="Persistence service temporarily unavailable") from exc
