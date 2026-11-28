"""Small revocable browser sessions for the local Codax API."""
from contextlib import closing
import hmac
import os
from pathlib import Path
from secrets import token_urlsafe
import sqlite3
import time

COOKIE_NAME = "codax_session"
TTL = 3600


def _path() -> Path:
    configured = os.getenv("CODAX_SESSIONS_DB")
    return Path(configured) if configured else Path.home() / ".codax" / "sessions.sqlite3"


def _digest(token: str, session_id: str) -> str | None:
    if len(session_id) != 43 or not session_id.isascii():
        return None
    return hmac.new(token.encode(), session_id.encode("ascii"), "sha256").hexdigest()


def create(token: str, previous: str) -> str | None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    session_id = token_urlsafe(32)
    digest = _digest(token, session_id)
    old_digest = _digest(token, previous)
    now = int(time.time())
    with closing(sqlite3.connect(path, timeout=2)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS sessions (digest TEXT PRIMARY KEY, expiry INTEGER NOT NULL)")
        db.execute("DELETE FROM sessions WHERE expiry <= ? OR digest = ?", (now, old_digest))
        created = db.execute("""
            INSERT INTO sessions (digest, expiry)
            SELECT ?, ? WHERE (SELECT COUNT(*) FROM sessions) < 512
        """, (digest, now + TTL))
        return session_id if created.rowcount == 1 else None


def valid(token: str, session_id: str) -> bool:
    digest = _digest(token, session_id)
    if digest is None or not _path().is_file():
        return False
    with closing(sqlite3.connect(_path(), timeout=2)) as db:
        return db.execute("SELECT 1 FROM sessions WHERE digest = ? AND expiry > ?",
                          (digest, int(time.time()))).fetchone() is not None


def revoke(token: str, session_id: str) -> None:
    digest = _digest(token, session_id)
    if digest is None or not _path().is_file():
        return
    with closing(sqlite3.connect(_path(), timeout=2)) as db, db:
        db.execute("DELETE FROM sessions WHERE digest = ?", (digest,))
