"""Application configuration — loads from .env file."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    def __init__(self) -> None:
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

        self.whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "base")
        self.whisper_device: str = os.getenv("WHISPER_DEVICE", "cpu")
        self.whisper_compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

        self.pollinations_base_url: str = os.getenv(
            "POLLINATIONS_BASE_URL", "https://image.pollinations.ai/prompt"
        )
        self.default_tts_voice: str = os.getenv(
            "DEFAULT_TTS_VOICE", "hi-IN-SwaraNeural"
        )
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def validate_settings() -> list[str]:
    """Return list of configuration error strings (empty = all good)."""
    errors: list[str] = []
    # No mandatory settings to validate right now, Ollama relies on local defaults
    return errors
