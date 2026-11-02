from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)


def test_health_reports_service_and_ai_configuration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "jarvis-dev-local"
    assert payload["ai_configured"] is False
    assert payload["model"]


def test_chat_uses_local_mode_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/api/chat", json={"message": "Ajude-me com Python"})

    assert response.status_code == 200
    assert response.json()["mode"] == "local"
    assert "pytest" in response.json()["reply"]
    assert "OPENAI_API_KEY" not in response.json()["reply"]


def test_local_mode_explains_its_limits(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/api/chat", json={"message": "Oi"})

    assert response.status_code == 200
    assert response.json()["mode"] == "local"
    assert "sem chave de API" in response.json()["reply"]


def test_chat_rejects_blank_message(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422
    assert "vazia" in response.json()["detail"]


def test_chat_returns_mocked_ai_reply(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class FakeResponse:
        output_text = "Resposta simulada para o teste."

    class FakeResponses:
        async def create(self, **kwargs):
            assert kwargs["input"] == "Explique APIs REST"
            assert kwargs["max_output_tokens"] == 900
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(main, "AsyncOpenAI", FakeClient)

    response = client.post("/api/chat", json={"message": "  Explique APIs REST  "})

    assert response.status_code == 200
    assert response.json()["reply"] == "Resposta simulada para o teste."
    assert response.json()["mode"] == "openai"
