import pytest


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("VT_API_KEY", "test-vt-key")
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://test.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "test-token")
