import logging
import os
from typing import Any

logger = logging.getLogger("codax.security")


def parse_allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or ["http://127.0.0.1:5173", "http://localhost:5173"]


def is_local_host(host: str | None) -> bool:
    return bool(host) and host.lower().replace("[::1]", "::1") in {"127.0.0.1", "::1", "testclient", "localhost"}


def is_valid_access_token(token: str | None) -> bool:
    value = (token or "").strip()
    return bool(value) and len(value) >= 32


def log_access_event(event: str, **context: Any) -> None:
    payload = {"event": event, **context}
    logger.info("access_event", extra=payload)
