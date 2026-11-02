"""Static analysis API tests: mocked GitHub transport; no live network, no code execution."""
import base64

import httpx
import pytest
from fastapi.testclient import TestClient

from app import code_inspection, github_readonly, main


def public_repo(*, private=False):
    return {
        "name": "sample-repo",
        "owner": {"login": "juniordev830"},
        "private": private,
        "default_branch": "main",
    }


def fake_github(monkeypatch, handler):
    monkeypatch.setenv("CODAX_GITHUB_OWNER", "juniordev830")
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        github_readonly, "_client_factory",
        lambda: httpx.AsyncClient(transport=transport),
    )
    monkeypatch.setattr(
        code_inspection, "_client_factory",
        lambda: httpx.AsyncClient(transport=transport),
    )
    return TestClient(main.app)


def test_file_list_filters_sensitive_paths_large_files_and_symlinks(monkeypatch):
    def handler(request):
        assert request.url.host == "api.github.com"
        if request.url.path == "/repos/juniordev830/sample-repo":
            return httpx.Response(200, json=public_repo())
        assert request.url.path == "/repos/juniordev830/sample-repo/git/trees/main"
        assert request.url.params["recursive"] == "1"
        return httpx.Response(200, json={"tree": [
            {"type": "blob", "path": "src/main.py", "size": 20, "mode": "100644"},
            {"type": "blob", "path": ".env.py", "size": 30, "mode": "100644"},
            {"type": "blob", "path": "src/api_token.py", "size": 20, "mode": "100644"},
            {"type": "blob", "path": "src/image.png", "size": 20, "mode": "100644"},
            {"type": "blob", "path": "src/big.js", "size": 90000, "mode": "100644"},
            {"type": "blob", "path": "src/alias.py", "size": 20, "mode": "120000"},
            {"type": "tree", "path": "src", "size": 0},
        ], "truncated": False})
    with fake_github(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/sample-repo/files")
        assert response.status_code == 200
        assert response.json()["files"] == [{"path": "src/main.py", "size": 20}]
        assert response.json()["scope"] == "public-source-read-only"


def test_selected_source_generates_deterministic_findings_without_ai(monkeypatch):
    source = "def f(x):\n    eval(x)\n    # TODO: document\n"
    raw = source.encode("utf-8")
    def handler(request):
        if request.url.path == "/repos/juniordev830/sample-repo":
            return httpx.Response(200, json=public_repo())
        assert request.url.path == "/repos/juniordev830/sample-repo/contents/src/main.py"
        return httpx.Response(200, json={
            "type": "file", "size": len(raw), "encoding": "base64",
            "content": base64.b64encode(raw).decode("ascii"),
        })
    with fake_github(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/sample-repo/source", params={"path": "src/main.py"})
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == source
        assert data["external_ai_used"] is False
        assert [(f["line"], f["title"]) for f in data["review"]["findings"]] == [
            (2, "Uso de eval"), (3, "Pendência no código")
        ]


@pytest.mark.parametrize("path", [
    "../secret.py", "/root.py", "src/../app.py", "src//app.py",
    ".github/workflows/build.py", "src/token.py", "src/credentials.js",
    "src/password_helper.py", "node_modules/library.js", "src/data.png",
    "src\\main.py",
])
def test_invalid_paths_rejected_without_upstream_call(monkeypatch, path):
    def handler(request):
        raise AssertionError("GitHub should not be called for invalid path")
    with fake_github(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/sample-repo/source", params={"path": path})
        assert response.status_code == 422
    main._buckets.clear()


def test_private_repo_not_exposed(monkeypatch):
    def handler(request):
        return httpx.Response(200, json=public_repo(private=True))
    with fake_github(monkeypatch, handler) as client:
        assert client.get("/api/github/repos/sample-repo/files").status_code == 404
        assert client.get("/api/github/repos/sample-repo/source", params={"path": "main.py"}).status_code == 404
    main._buckets.clear()


@pytest.mark.parametrize("upstream", [
    {"type": "symlink", "size": 16, "encoding": "base64", "content": "YQ=="},
    {"type": "file", "size": 50000, "encoding": "base64", "content": "YQ=="},
])
def test_symlink_or_oversize_not_read(monkeypatch, upstream):
    def handler(request):
        if request.url.path == "/repos/juniordev830/sample-repo":
            return httpx.Response(200, json=public_repo())
        return httpx.Response(200, json=upstream)
    with fake_github(monkeypatch, handler) as client:
        response = client.get("/api/github/repos/sample-repo/source", params={"path": "main.py"})
        assert response.status_code in {413, 422}


def test_non_utf8_content_not_exposed(monkeypatch):
    def handler(request):
        if request.url.path == "/repos/juniordev830/sample-repo":
            return httpx.Response(200, json=public_repo())
        return httpx.Response(200, json={
            "type": "file", "size": 1, "encoding": "base64", "content": "/w=="
        })
    with fake_github(monkeypatch, handler) as client:
        assert client.get("/api/github/repos/sample-repo/source", params={"path": "main.py"}).status_code == 422


def test_truncated_tree_is_explicitly_rejected(monkeypatch):
    def handler(request):
        if request.url.path == "/repos/juniordev830/sample-repo":
            return httpx.Response(200, json=public_repo())
        return httpx.Response(200, json={"tree": [], "truncated": True})
    with fake_github(monkeypatch, handler) as client:
        assert client.get("/api/github/repos/sample-repo/files").status_code == 413


def test_code_review_get_remains_protected_remotely(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.25", 123)) as client:
            response = client.get("/api/github/repos/sample-repo/source", params={"path": "main.py"})
            assert response.status_code == 503
    finally:
        main._buckets.clear()
