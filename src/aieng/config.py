"""Settings read from the environment, never from code.

Keys live in .env (git-ignored). .env.example lists every variable with an empty value,
so a fresh checkout shows what has to be filled in without leaking anything.
"""

import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    # Local models through Ollama are the default: free, offline, no limits.
    ollama_url: str = "http://localhost:11434"
    local_model: str = ""
    # Hosted providers are optional. An empty key means "not configured", not an error.
    gemini_api_key: str = ""
    anthropic_api_key: str = ""

    def has(self, provider: str) -> bool:
        """True when the provider's key is set, e.g. settings.has("gemini")."""
        return bool(getattr(self, f"{provider}_api_key", ""))


def load_settings(env_file: Path | None = None) -> Settings:
    """Real environment variables win over .env, as in production.

    The file is read into a dict instead of being loaded into os.environ, so loading
    settings has no side effects and tests cannot leak keys into each other.
    """
    path = env_file or PROJECT_ROOT / ".env"
    file_values = dotenv_values(path) if path.exists() else {}

    def get(name: str, default: str = "") -> str:
        return os.environ.get(name) or file_values.get(name) or default

    return Settings(
        ollama_url=get("OLLAMA_URL", Settings.model_fields["ollama_url"].default),
        local_model=get("LOCAL_MODEL"),
        gemini_api_key=get("GEMINI_API_KEY"),
        anthropic_api_key=get("ANTHROPIC_API_KEY"),
    )
