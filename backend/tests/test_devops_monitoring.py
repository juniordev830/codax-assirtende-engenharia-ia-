from app.devops_monitoring import filter_pipelines, summarize_pipelines
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
