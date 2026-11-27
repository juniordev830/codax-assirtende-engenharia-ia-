import pytest

from app import main


@pytest.fixture(autouse=True)
def isolate_api_access_state(monkeypatch):
    # TestClient represents a local development client. Production behavior is
    # tested explicitly in test_access.py; ordinary API tests opt into dev mode.
    monkeypatch.setenv("CODAX_ENV", "development")
    main._buckets.clear()
    yield
    main._buckets.clear()
