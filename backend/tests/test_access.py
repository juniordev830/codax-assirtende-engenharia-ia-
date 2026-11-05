from fastapi.testclient import TestClient
from app import main

def test_remote_access_fails_closed_without_token(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    with TestClient(main.app, client=("192.0.2.1", 123)) as client:
        assert client.post("/api/chat", json={"message": "oi"}).status_code == 503

def test_session_and_rate_limit(monkeypatch):
    token = "test-access-token-" * 3
    monkeypatch.setenv("CODAX_ACCESS_TOKEN", token)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    main._buckets.clear()
    with TestClient(main.app) as client:
        assert client.post("/api/chat", json={"message": "oi"}).status_code == 401
        origin = {"Origin": "http://localhost:5173"}
        assert client.post("/api/session", json={"token": token}, headers=origin).status_code == 200
        assert client.post("/api/chat", json={"message": "oi"}, headers=origin).status_code == 200
        assert client.post("/api/chat", json={"message": "oi"}, headers={"Origin": "https://other.example"}).status_code == 403
        for _ in range(25):
            response = client.post("/api/chat", json={"message": "oi"}, headers=origin)
        assert response.status_code == 429
    main._buckets.clear()

def test_short_configured_token_is_rejected_for_bearer_and_session(monkeypatch):
    monkeypatch.setenv("CODAX_ACCESS_TOKEN", "too-short")
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.2", 123)) as client:
            assert client.post("/api/chat", json={"message": "oi"}, headers={"Authorization": "Bearer too-short"}).status_code == 503
            assert client.post("/api/session", json={"token": "too-short"}, headers={"Origin": "http://localhost:5173"}).status_code == 503
    finally:
        main._buckets.clear()

def test_bearer_requires_scheme_and_unicode_login_is_handled(monkeypatch):
    token = "valid-test-access-token-" * 2
    monkeypatch.setenv("CODAX_ACCESS_TOKEN", token)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.3", 123)) as client:
            assert client.post("/api/chat", json={"message": "oi"}, headers={"Authorization": token}).status_code == 401
            assert client.post("/api/chat", json={"message": "oi"}, headers={"Authorization": "Bearer " + token}).status_code == 200
            response = client.post("/api/session", json={"token": "inválido"}, headers={"Origin": "http://localhost:5173"})
            assert response.status_code == 401
    finally:
        main._buckets.clear()


def test_ambiguous_authorization_headers_are_rejected(monkeypatch):
    token = "codax-test-token-" * 3
    monkeypatch.setenv("CODAX_ACCESS_TOKEN", token)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    main._buckets.clear()
    try:
        with TestClient(main.app, client=("192.0.2.10", 123)) as client:
            duplicate = client.post(
                "/api/chat", json={"message": "oi"},
                headers=[
                    ("Authorization", "Bearer " + token),
                    ("Authorization", "Bearer invalid"),
                ],
            )
            assert duplicate.status_code == 401

            combined = client.post(
                "/api/chat", json={"message": "oi"},
                headers={"Authorization": "Bearer " + token + ", Bearer invalid"},
            )
            assert combined.status_code == 401

            oversized = client.post(
                "/api/chat", json={"message": "oi"},
                headers={"Authorization": "Bearer " + ("a" * 8200)},
            )
            assert oversized.status_code == 401

            allowed = client.post(
                "/api/chat", json={"message": "oi"},
                headers={"Authorization": "Bearer " + token},
            )
            assert allowed.status_code == 200
    finally:
        main._buckets.clear()
