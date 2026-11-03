"""Read-only pipeline summary module adapted from devops-control-center.

The source project's demo data is deliberately not presented as live GitHub status.
No credentials, code execution or repository mutations are performed.
"""
from collections import Counter

VALID_STATUSES = frozenset({"success", "failure", "running"})

def filter_pipelines(pipelines, status=None, repository=None):
    if status is not None and status not in VALID_STATUSES:
        raise ValueError("invalid status")
    repository = (repository or "").strip().lower()
    if len(repository) > 100:
        raise ValueError("repository filter too long")
    return [
        item for item in pipelines
        if (status is None or item.get("status") == status)
        and (not repository or repository in str(item.get("repository", "")).lower())
    ]

def summarize_pipelines(pipelines):
    counts = Counter(item.get("status") for item in pipelines)
    result = {status: counts[status] for status in ("success", "failure", "running")}
    completed = result["success"] + result["failure"]
    return {
        "total": len(pipelines),
        "counts": result,
        "successRate": round(result["success"] / completed * 100, 2) if completed else None,
    }


def workflow_status(state, conclusion):
    """Map only known upstream states; absent or new states remain unknown."""
    if not isinstance(state, str):
        return "unknown"
    if state in {"queued", "in_progress", "waiting", "pending", "requested"}:
        return "running"
    if state != "completed" or not isinstance(conclusion, str):
        return "unknown"
    if conclusion == "success":
        return "success"
    if conclusion in {"failure", "timed_out", "startup_failure"}:
        return "failure"
    return "unknown"
