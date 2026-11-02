"""AI code review tests: all provider and GitHub calls are simulated."""
import pytest
from fastapi.testclient import TestClient

from app import ai_code_review, main

SHA = "a" * 40
REQUEST = {
    "path": "src/main.py",
    "expected_sha": SHA,
    "confirmed_external_processing": True,
}


@pytest.fixture
def api(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    with TestClient(main.app) as client:
        yield client
    main._buckets.clear()


def test_requires_explicit_external_consent_without_touching_provider(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    async def forbidden(*args):
        raise AssertionError("Should not fetch code without explicit consent")
    monkeypatch.setattr(ai_code_review, "inspect_public_source", forbidden)
    url = "/api/github/repos/sample-repo/ai-review"
    assert api.post(url, json={k: v for k, v in REQUEST.items() if k != "confirmed_external_processing"}).status_code == 422
    assert api.post(url, json={**REQUEST, "confirmed_external_processing": False}).status_code == 422
    assert api.post(url, json={**REQUEST, "confirmed_external_processing": True, "token": "bad"}).status_code == 422


def test_unconfigured_api_returns_503_before_fetching_github(api, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    async def forbidden(*args):
        raise AssertionError("Should not fetch code when provider disabled")
    monkeypatch.setattr(ai_code_review, "inspect_public_source", forbidden)
    response = api.post("/api/github/repos/sample-repo/ai-review", json=REQUEST)
    assert response.status_code == 503
    assert "desativada" in response.json()["detail"]


def test_sha_mismatch_rejected_before_model_call(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-token")
    async def file_result(*args):
        return {"content": "print('safe')", "sha": "b" * 40}
    monkeypatch.setattr(ai_code_review, "inspect_public_source", file_result)
    response = api.post("/api/github/repos/sample-repo/ai-review", json=REQUEST)
    assert response.status_code == 409
    assert "mudou" in response.json()["detail"]


@pytest.mark.parametrize("content", [
    "a" * 12001,
    "-----BEGIN PRIVATE KEY-----\nsecret material\n-----END PRIVATE KEY-----",
    "API_KEY = 'this_is_a_realistic_long_token'",
    "sk-proj-abcdefghijklmnopqrstuvwxyz012345",
])
def test_source_too_long_or_probable_secrets_never_sent(api, monkeypatch, content):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-token")
    async def file_result(*args):
        return {"content": content, "sha": SHA}
    monkeypatch.setattr(ai_code_review, "inspect_public_source", file_result)
    response = api.post("/api/github/repos/sample-repo/ai-review", json=REQUEST)
    assert response.status_code in (413, 422)


def test_ai_receives_only_selected_file_and_returns_non_mutating_recommendation(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    monkeypatch.setenv("OPENAI_MODEL", "fake-review-model")
    observed = {}
    async def file_result(repo, path):
        observed["selected"] = (repo, path)
        return {"content": "def f():\n    return 1\n", "sha": SHA}

    class FakeResponse:
        output_text = "Função simples; adicione um teste."

    class FakeResponses:
        async def create(self, **kwargs):
            observed["request"] = kwargs
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            observed["client_options"] = kwargs
            self.responses = FakeResponses()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(ai_code_review, "inspect_public_source", file_result)
    monkeypatch.setattr(ai_code_review, "AsyncOpenAI", FakeClient)
    response = api.post("/api/github/repos/sample-repo/ai-review", json=REQUEST)
    assert response.status_code == 200
    data = response.json()
    assert observed["selected"] == ("sample-repo", "src/main.py")
    assert observed["request"]["model"] == "fake-review-model"
    assert observed["request"]["max_output_tokens"] == 1100
    assert "return 1" in observed["request"]["input"]
    assert "não confiável" in observed["request"]["instructions"]
    assert data["modified_files"] is False
    assert data["external_ai_used"] is True
    assert data["files_analyzed"] == 1
    assert "teste" in data["analysis"]


def test_invalid_path_and_sha_rejected_without_external_call(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-token")
    async def forbidden(*args):
        raise AssertionError("Should not fetch invalid source")
    monkeypatch.setattr(ai_code_review, "inspect_public_source", forbidden)
    url = "/api/github/repos/sample-repo/ai-review"
    assert api.post(url, json={**REQUEST, "path": "../secret.py"}).status_code == 422
    assert api.post(url, json={**REQUEST, "expected_sha": "x" * 40}).status_code == 422
    assert api.post("/api/github/repos/bad%20repo/ai-review", json=REQUEST).status_code == 422


def test_remote_access_to_ai_review_requires_auth(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.45", 123)) as remote:
            result = remote.post("/api/github/repos/sample-repo/ai-review", json=REQUEST)
            assert result.status_code == 503
    finally:
        main._buckets.clear()
