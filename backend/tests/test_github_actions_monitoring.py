"""Mocked public GitHub Actions integration tests (no network)."""
import httpx
from fastapi.testclient import TestClient
from app import github_actions_monitoring, main

def test_actions_returns_live_runs_without_token(monkeypatch):
    monkeypatch.setenv("CODAX_GITHUB_OWNER", "juniordev830")
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    def handler(request):
        if request.url.path.endswith("/actions/runs"):
            return httpx.Response(200, json={"workflow_runs": [
                {"id": 1, "name": "CI", "status": "completed", "conclusion": "success"},
                {"id": 2, "name": "CI", "status": "completed", "conclusion": "failure"},
                {"id": 3, "name": "CI", "status": "in_progress", "conclusion": None},
            ]})
        return httpx.Response(200, json={
            "owner": {"login": "juniordev830"}, "name": "codax", "private": False,
        })
    monkeypatch.setattr(github_actions_monitoring, "_client_factory",
                        lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    with TestClient(main.app) as client:
        response = client.get("/api/github/repos/codax/actions")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "github-actions-public"
        assert data["summary"]["counts"]["success"] == 1
        assert data["summary"]["counts"]["failure"] == 1
        assert data["summary"]["counts"]["running"] == 1
        assert data["summary"]["successRate"] == 50.0
    main._buckets.clear()

def test_actions_invalid_name_rejected(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    with TestClient(main.app) as client:
        assert client.get("/api/github/repos/bad%20name/actions").status_code == 422
    main._buckets.clear()


def actions_client(monkeypatch, handler):
    monkeypatch.setenv("CODAX_GITHUB_OWNER", "juniordev830")
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    monkeypatch.setattr(github_actions_monitoring, "_client_factory",
                        lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    return TestClient(main.app)


def test_cancelled_and_skipped_runs_do_not_lower_success_rate(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"workflow_runs": [
            {"id": 1, "status": "completed", "conclusion": "success"},
            {"id": 2, "status": "completed", "conclusion": "cancelled"},
            {"id": 3, "status": "completed", "conclusion": "skipped"},
            {"id": 4},
        ]})
    with actions_client(monkeypatch, handler) as client:
        data = client.get("/api/github/repos/codax/actions").json()
    assert [run["status"] for run in data["runs"]] == ["success", "unknown", "unknown", "unknown"]
    assert data["summary"]["counts"] == {"success": 1, "failure": 0, "running": 0, "unknown": 3}
    assert data["summary"]["successRate"] == 100.0
    main._buckets.clear()


def test_forty_repositories_use_one_unauthenticated_upstream_request_each(monkeypatch):
    requests = []
    def handler(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.url.host == "api.github.com"
        assert request.url.path.startswith("/repos/juniordev830/sample-")
        assert request.url.path.endswith("/actions/runs")
        assert "authorization" not in request.headers
        assert request.url.params["per_page"] == "30"
        return httpx.Response(200, json={"workflow_runs": []})
    with actions_client(monkeypatch, handler) as client:
        for index in range(40):
            response = client.get(f"/api/github/repos/sample-{index}/actions")
            assert response.status_code == 200
            assert response.json()["summary"]["successRate"] is None
    assert len(requests) == 40
    main._buckets.clear()


def test_private_or_missing_repository_is_not_reported_as_healthy(monkeypatch):
    with actions_client(monkeypatch, lambda request: httpx.Response(404)) as client:
        response = client.get("/api/github/repos/private/actions")
        assert response.status_code == 404
        assert "runs" not in response.json()
    main._buckets.clear()


def test_rate_limit_and_malformed_payload_are_controlled_errors(monkeypatch):
    for upstream_status, payload, expected in [
        (403, {}, 503), (429, {}, 503),
        (200, {"workflow_runs": None}, 502), (200, [], 502),
    ]:
        def handler(request):
            return httpx.Response(upstream_status, json=payload)
        with actions_client(monkeypatch, handler) as client:
            response = client.get("/api/github/repos/codax/actions")
            assert response.status_code == expected
            assert "runs" not in response.json()
        main._buckets.clear()


def test_actions_endpoint_keeps_remote_access_control(monkeypatch):
    def handler(request):
        raise AssertionError("Remote unauthenticated requests must not reach GitHub")
    with actions_client(monkeypatch, handler):
        with TestClient(main.app, client=("192.0.2.55", 123)) as remote:
            assert remote.get("/api/github/repos/codax/actions").status_code == 503
    main._buckets.clear()
