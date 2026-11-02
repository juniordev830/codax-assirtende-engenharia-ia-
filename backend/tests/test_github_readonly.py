"""Public GitHub API tests: real HTTP is never used."""
import base64

import httpx
from fastapi.testclient import TestClient

from app import github_readonly, main


def repo(name, owner="juniordev830", private=False):
    return {
        "name": name,
        "owner": {"login": owner},
        "private": private,
        "description": "Projeto de testes",
        "language": "Python",
        "updated_at": "2026-11-02T10:00:00Z",
        "html_url": "https://evil.example/not-used",
    }


def client_with_mock(monkeypatch, handler):
    monkeypatch.setenv("CODAX_GITHUB_OWNER", "juniordev830")
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        github_readonly, "_client_factory",
        lambda: httpx.AsyncClient(transport=transport),
    )
    return TestClient(main.app)


def test_repo_list_excludes_private_and_other_owner(monkeypatch):
    def handler(request):
        assert request.url.host == "api.github.com"
        assert request.url.path == "/users/juniordev830/repos"
        assert request.url.params["per_page"] == "100"
        return httpx.Response(200, json=[
            repo("codax"), repo("private", private=True),
            repo("wrong-owner", owner="someone-else"), repo("../unsafe"),
        ])

    with client_with_mock(monkeypatch, handler) as client:
        response = client.get("/api/github/repos")
        assert response.status_code == 200
        payload = response.json()
        assert payload["scope"] == "public-read-only"
        assert [item["name"] for item in payload["repositories"]] == ["codax"]
        assert payload["repositories"][0]["html_url"] == "https://github.com/juniordev830/codax"
    main._buckets.clear()


def test_repository_summary_returns_readme_preview_as_plain_text(monkeypatch):
    readme_text = "# Codax\n<script>alert('not rendered')</script>"
    readme_bytes = readme_text.encode()

    def handler(request):
        if request.url.path == "/repos/juniordev830/codax":
            return httpx.Response(200, json=repo("codax"))
        if request.url.path == "/repos/juniordev830/codax/readme":
            return httpx.Response(200, json={
                "encoding": "base64",
                "size": len(readme_bytes),
                "content": base64.b64encode(readme_bytes).decode(),
            })
        return httpx.Response(404)

    with client_with_mock(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/codax")
        assert response.status_code == 200
        assert response.json()["readme_preview"] == readme_text
        assert response.json()["readme_truncated"] is False
    main._buckets.clear()


def test_missing_readme_is_not_an_error(monkeypatch):
    def handler(request):
        if request.url.path.endswith("/readme"):
            return httpx.Response(404)
        return httpx.Response(200, json=repo("empty-readme"))

    with client_with_mock(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/empty-readme")
        assert response.status_code == 200
        assert response.json()["readme_preview"] == ""
    main._buckets.clear()


def test_untrusted_name_rejected_before_upstream_request(monkeypatch):
    def handler(request):
        raise AssertionError("Should not call upstream")

    with client_with_mock(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/bad%20repo")
        assert response.status_code == 422
    main._buckets.clear()


def test_upstream_rate_limit_returns_controlled_error(monkeypatch):
    def handler(request):
        return httpx.Response(403, json={"message": "rate limited"})

    with client_with_mock(monkeypatch, handler) as client:
        response = client.get("/api/github/repos")
        assert response.status_code == 503
        assert "GitHub" in response.json()["detail"]
    main._buckets.clear()


def test_public_github_routes_still_require_codax_remote_auth(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.55", 123)) as client:
            assert client.get("/api/github/repos").status_code == 503
    finally:
        main._buckets.clear()


def test_github_get_routes_are_rate_limited(monkeypatch):
    def handler(request):
        return httpx.Response(200, json=[])

    with client_with_mock(monkeypatch, handler) as client:
        responses = [client.get("/api/github/repos") for _ in range(21)]
        assert all(response.status_code == 200 for response in responses[:20])
        assert responses[20].status_code == 429
    main._buckets.clear()
