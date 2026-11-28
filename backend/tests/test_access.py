from fastapi.testclient import TestClient
from app import main

def test_remote_access_fails_closed_without_token(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    main._buckets.clear()
    with TestClient(main.app, client=("192.0.2.1", 123)) as client:
        assert client.post("/api/chat", json={"message": "oi"}).status_code == 503

def test_session_and_rate_limit(monkeypatch, tmp_path):
    monkeypatch.setenv("CODAX_SESSIONS_DB", str(tmp_path / "sessions.db"))
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


def test_loopback_without_token_requires_explicit_development_mode(monkeypatch):
    monkeypatch.delenv("CODAX_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("CODAX_ENV", raising=False)
    main._buckets.clear()
    with TestClient(main.app) as client:
        response = client.post("/api/chat", json={"message": "oi"})
        assert response.status_code == 503

    monkeypatch.setenv("CODAX_ENV", "development")
    main._buckets.clear()
    with TestClient(main.app) as client:
        response = client.post("/api/chat", json={"message": "oi"})
        assert response.status_code == 200

    monkeypatch.setenv("CODAX_ENV", "production")
    main._buckets.clear()
    with TestClient(main.app) as client:
        response = client.post("/api/chat", json={"message": "oi"})
        assert response.status_code == 503
    main._buckets.clear()


def test_logout_revokes_the_copied_session_and_preserves_other_sessions(monkeypatch, tmp_path):
    token = "fixture-token-" * 3
    monkeypatch.setenv("CODAX_ACCESS_TOKEN", token)
    monkeypatch.setenv("CODAX_SESSIONS_DB", str(tmp_path / "sessions.db"))
    main._buckets.clear()
    origin = {"Origin": "http://localhost:5173"}
    with TestClient(main.app) as first, TestClient(main.app) as second, TestClient(main.app) as copied:
        assert first.post("/api/session", json={"token": token}, headers=origin).status_code == 200
        assert second.post("/api/session", json={"token": token}, headers=origin).status_code == 200
        copied.cookies.set("codax_session", first.cookies.get("codax_session"))
        assert first.post("/api/session/logout", headers={"Origin": "https://other.example"}).status_code == 403
        assert first.post("/api/session/logout", headers=origin).status_code == 200
        assert copied.get("/api/capabilities").status_code == 401
        assert second.get("/api/capabilities").status_code == 200
    main._buckets.clear()
