"""SQLite persistence adapter for the local URL-shortener demo.

Production deployments should use PostgreSQL with migrations and connection pooling.
"""
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).with_name("shortener.db")
DB_PATH = Path(os.getenv("SHORTENER_DB_PATH", str(DEFAULT_DB_PATH)))
BUSY_TIMEOUT_MS = 5000

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=BUSY_TIMEOUT_MS / 1000)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def initialize():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                short_code TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
                click_count INTEGER NOT NULL DEFAULT 0 CHECK(click_count >= 0)
            )
        """)
