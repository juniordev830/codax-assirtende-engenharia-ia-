"""Persistent task tracking and local API usage accounting for J.A.R.V.I.S. Dev."""

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DATA_DIR = Path(os.getenv("JARVIS_DATA_DIR", Path(__file__).resolve().parents[1] / ".jarvis_data"))
DB_PATH = DATA_DIR / "jarvis.sqlite3"
TASK_STATES = {
    "planned", "running", "waiting_approval", "completed", "failed", "cancelled"
}


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_storage() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                state TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                steps_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                estimated_cost_usd REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_task(title: str, description: str) -> dict[str, Any]:
    task_id = str(uuid.uuid4())
    now = _now()
    with _connect() as conn:
        conn.execute(
            """INSERT INTO tasks
               (id, title, description, state, progress, steps_json, created_at, updated_at)
               VALUES (?, ?, ?, 'planned', 0, '[]', ?, ?)""",
            (task_id, title.strip(), description.strip(), now, now),
        )
    return get_task(task_id)  # type: ignore[return-value]


def _task(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["steps"] = json.loads(item.pop("steps_json"))
    return item


def get_task(task_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _task(row) if row else None


def list_tasks(limit: int = 50) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_task(row) for row in rows]


def update_task(task_id: str, *, state: str | None = None,
                progress: int | None = None,
                steps: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    if state is not None and state not in TASK_STATES:
        raise ValueError("Estado de tarefa inválido.")
    if progress is not None and not 0 <= progress <= 100:
        raise ValueError("O progresso deve estar entre 0 e 100.")
    current = get_task(task_id)
    if current is None:
        return None
    new_state = state if state is not None else current["state"]
    new_progress = progress if progress is not None else current["progress"]
    new_steps = steps if steps is not None else current["steps"]
    with _connect() as conn:
        conn.execute(
            """UPDATE tasks SET state=?, progress=?, steps_json=?, updated_at=?
               WHERE id=?""",
            (new_state, new_progress, json.dumps(new_steps, ensure_ascii=False),
             _now(), task_id),
        )
    return get_task(task_id)


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def month_spend_usd(month: str | None = None) -> float:
    month = month or current_month()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(estimated_cost_usd), 0) AS total FROM api_usage WHERE month=?",
            (month,),
        ).fetchone()
    return float(row["total"])


def record_api_usage(model: str, input_tokens: int, output_tokens: int,
                     input_price_per_million: float, output_price_per_million: float) -> float:
    input_tokens = max(0, int(input_tokens))
    output_tokens = max(0, int(output_tokens))
    cost = (
        input_tokens * input_price_per_million
        + output_tokens * output_price_per_million
    ) / 1_000_000
    with _connect() as conn:
        conn.execute(
            """INSERT INTO api_usage
               (month, model, input_tokens, output_tokens, estimated_cost_usd, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (current_month(), model, input_tokens, output_tokens, cost, _now()),
        )
    return cost
