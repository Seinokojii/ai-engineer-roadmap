from aieng.config import load_settings


def test_defaults_without_env(tmp_path, monkeypatch):
    for var in ("OLLAMA_URL", "LOCAL_MODEL", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    s = load_settings(env_file=tmp_path / "missing.env")
    assert s.ollama_url == "http://localhost:11434"
    assert not s.has("gemini")
    assert not s.has("anthropic")


def test_key_from_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
    s = load_settings(env_file=env)
    assert s.has("gemini")
    assert s.gemini_api_key == "test-key"
