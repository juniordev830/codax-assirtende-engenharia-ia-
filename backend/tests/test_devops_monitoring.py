from app.devops_monitoring import filter_pipelines, summarize_pipelines, workflow_status
import pytest

PIPELINES = [
    {"repository": "sample-api", "status": "success"},
    {"repository": "sample-web", "status": "failure"},
    {"repository": "sample-worker", "status": "running"},
]

def test_filter_status_and_repository():
    assert filter_pipelines(PIPELINES, "failure", "WEB") == [PIPELINES[1]]

def test_reject_invalid_filters():
    with pytest.raises(ValueError):
        filter_pipelines(PIPELINES, "unknown")
    with pytest.raises(ValueError):
        filter_pipelines(PIPELINES, repository="x" * 101)

def test_summary():
    assert summarize_pipelines(PIPELINES) == {
        "total": 3,
        "counts": {"success": 1, "failure": 1, "running": 1},
        "successRate": 50.0,
    }

def test_no_completed_runs():
    assert summarize_pipelines([PIPELINES[2]])["successRate"] is None


@pytest.mark.parametrize(("state", "conclusion", "expected"), [
    ("completed", "success", "success"),
    ("completed", "failure", "failure"),
    ("completed", "timed_out", "failure"),
    ("completed", "startup_failure", "failure"),
    ("completed", "cancelled", "unknown"),
    ("completed", "skipped", "unknown"),
    ("completed", "neutral", "unknown"),
    ("completed", "action_required", "unknown"),
    ("completed", None, "unknown"),
    ("completed", {"unexpected": True}, "unknown"),
    ("completed", "new-conclusion", "unknown"),
    ("queued", None, "running"),
    ("in_progress", None, "running"),
    ("waiting", None, "running"),
    ("pending", None, "running"),
    ("requested", None, "running"),
    (None, None, "unknown"),
    ("new-state", "success", "unknown"),
    ([], None, "unknown"),
])
def test_workflow_status_preserves_unknown_and_cancelled_states(state, conclusion, expected):
    assert workflow_status(state, conclusion) == expected
