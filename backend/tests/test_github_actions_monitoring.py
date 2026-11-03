"""Mocked public GitHub Actions integration tests (no network)."""
import httpx
from fastapi.testclient import TestClient
from app import github_readonly, main

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
    monkeypatch.setattr(github_readonly, "_client_factory",
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
