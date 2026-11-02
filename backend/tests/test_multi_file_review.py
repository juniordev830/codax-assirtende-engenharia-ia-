"""Multi-file review tests never call GitHub or a paid AI provider."""
import json

import pytest
from fastapi.testclient import TestClient

from app import main, multi_file_review

SHA_A = "a" * 40
SHA_B = "b" * 40
FILES = [
    {"path": "src/a.py", "expected_sha": SHA_A},
    {"path": "src/b.py", "expected_sha": SHA_B},
]
URL = "/api/github/repos/project"


@pytest.fixture
def api(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    with TestClient(main.app) as client:
        yield client
    main._buckets.clear()


def mock_files(monkeypatch, files=None):
    entries = files or {
        "src/a.py": {"content": "def calc():\n    return 1\n", "sha": SHA_A},
        "src/b.py": {"content": "# TODO: test\n", "sha": SHA_B},
    }
    calls = []
    async def fetch(repo, path):
        calls.append((repo, path))
        entry = entries[path]
        return {
            "repository": repo, "path": path,
            "sha": entry["sha"], "content": entry["content"],
            "review": {"findings": [], "method": "heuristic"}
        }
    monkeypatch.setattr(multi_file_review, "inspect_public_source", fetch)
    return calls


def test_local_batch_reads_only_selected_files_and_uses_no_api(api, monkeypatch):
    calls = mock_files(monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = api.post(f"{URL}/review-batch", json={"files": FILES})
    assert response.status_code == 200
    data = response.json()
    assert data["file_count"] == 2
    assert data["external_ai_used"] is False
    assert data["modified_files"] is False
    assert [f["path"] for f in data["files"]] == ["src/a.py", "src/b.py"]
    assert calls == [("project", "src/a.py"), ("project", "src/b.py")]


@pytest.mark.parametrize("items", [
    [],
    FILES + FILES,
    [FILES[0], FILES[0]],
    [{"path": "../secret.py", "expected_sha": SHA_A}],
    [{"path": "src/a.py", "expected_sha": "bad"}],
    [{"path": "src/a.py", "expected_sha": SHA_A, "extra": "bad"}],
])
def test_invalid_selections_rejected_without_fetch(api, monkeypatch, items):
    calls = mock_files(monkeypatch)
    assert api.post(f"{URL}/review-batch", json={"files": items}).status_code == 422
    assert calls == []


def test_changed_sha_is_rejected(api, monkeypatch):
    calls = mock_files(monkeypatch)
    response = api.post(f"{URL}/review-batch", json={"files": [
        {"path": "src/a.py", "expected_sha": SHA_B}
    ]})
    assert response.status_code == 409
    assert calls == [("project", "src/a.py")]


def test_consent_and_preview_only_required_before_any_git_fetch(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    calls = mock_files(monkeypatch)
    payload = {"files": FILES, "preview_only": True, "confirmed_external_processing": True}
    for key in ("confirmed_external_processing", "preview_only"):
        bad = dict(payload)
        bad.pop(key)
        assert api.post(f"{URL}/diff-proposal", json=bad).status_code == 422
    assert api.post(f"{URL}/diff-proposal", json={**payload, "preview_only": False}).status_code == 422
    assert api.post(f"{URL}/diff-proposal", json={**payload, "confirmed_external_processing": False}).status_code == 422
    assert calls == []


def test_no_key_does_not_fetch_code(api, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    calls = mock_files(monkeypatch)
    response = api.post(f"{URL}/diff-proposal", json={
        "files": FILES, "preview_only": True, "confirmed_external_processing": True
    })
    assert response.status_code == 503
    assert calls == []


def test_detected_secrets_never_sent(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    mock_files(monkeypatch, {"src/a.py": {"content": "api_key = 'very_long_exposed_secret_value'\n", "sha": SHA_A}})
    response = api.post(f"{URL}/diff-proposal", json={
        "files": [FILES[0]], "preview_only": True, "confirmed_external_processing": True
    })
    assert response.status_code == 422


def test_ai_generates_preview_diffs_without_mutation(api, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("OPENAI_MODEL", "fake-model")
    calls = mock_files(monkeypatch)
    observed = {}

    class FakeResponse:
        output_text = json.dumps({
            "summary": "Acrescentar anotação de retorno.",
            "changes": [{
                "path": "src/a.py",
                "new_content": "def calc() -> int:\n    return 1\n",
                "reason": "Tipagem para legibilidade",
            }],
        })

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

    monkeypatch.setattr(multi_file_review, "AsyncOpenAI", FakeClient)
    response = api.post(f"{URL}/diff-proposal", json={
        "files": FILES, "preview_only": True, "confirmed_external_processing": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["modified_files"] is False
    assert data["preview_only"] is True
    assert data["external_ai_used"] is True
    assert len(data["proposals"]) == 1
    assert "--- a/src/a.py" in data["proposals"][0]["diff"]
    assert "+++ b/src/a.py" in data["proposals"][0]["diff"]
    assert "+def calc() -> int:" in data["proposals"][0]["diff"]
    assert observed["request"]["model"] == "fake-model"
    assert "não confiável" in observed["request"]["instructions"]
    assert calls == [("project", "src/a.py"), ("project", "src/b.py")]


@pytest.mark.parametrize("answer", [
    "not JSON",
    json.dumps({"summary": "ok", "changes": [{"path": "src/new.py", "new_content": "evil", "reason": "x"}]}),
    json.dumps({"summary": "ok", "changes": [{"path": "src/a.py", "new_content": "a" * 14000, "reason": "x"}]}),
    json.dumps({"summary": "ok", "changes": [
        {"path": "src/a.py", "new_content": "x", "reason": "x"},
        {"path": "src/a.py", "new_content": "x", "reason": "x"},
    ]}),
    json.dumps({"summary": "ok", "changes": [
        {"path": "src/a.py", "new_content": "password = 'long_password_value'\n", "reason": "x"}
    ]}),
])
def test_rejects_unsafe_model_changes(answer):
    source = [{"path": "src/a.py", "content": "print('ok')\n"}]
    with pytest.raises(Exception) as exc:
        multi_file_review.render_proposed_diffs(answer, source)
    assert exc.value.status_code == 502


def test_remote_routes_require_codax_auth(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.75", 8901)) as client:
            response = client.post(f"{URL}/review-batch", json={"files": FILES})
            assert response.status_code == 503
            response = client.post(f"{URL}/diff-proposal", json={
                "files": FILES, "preview_only": True, "confirmed_external_processing": True
            })
            assert response.status_code == 503
    finally:
        main._buckets.clear()
