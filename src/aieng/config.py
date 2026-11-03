"""Settings read from the environment, never from code.

Keys live in .env (git-ignored). .env.example lists every variable with an empty value,
so a fresh checkout shows what has to be filled in without leaking anything.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
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
    load_dotenv(env_file or PROJECT_ROOT / ".env", override=False)
    return Settings(
        ollama_url=os.getenv("OLLAMA_URL", Settings.model_fields["ollama_url"].default),
        local_model=os.getenv("LOCAL_MODEL", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
    )
