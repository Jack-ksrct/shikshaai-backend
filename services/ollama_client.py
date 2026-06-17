"""Ollama API client — local LLM integration."""

from __future__ import annotations

import requests
import json
from functools import lru_cache

from utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Ollama text generation client."""

    def __init__(self) -> None:
        from utils.config import get_settings
        settings = get_settings()
        self._url = f"{settings.ollama_base_url}/api/generate"
        self._model = settings.ollama_model
        logger.info(f"Ollama client initialized: url={self._url}, model={self._model}")

    def generate(self, prompt: str, max_retries: int = 1, format: str | None = None) -> str:
        """Generate text using Ollama. Returns response text string."""
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if format == "json":
            payload["format"] = "json"
        
        try:
            response = requests.post(self._url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as exc:
            logger.exception("Ollama generation failed")
            raise RuntimeError(f"Ollama generation failed: {exc}")


@lru_cache(maxsize=1)
def get_ollama_client() -> OllamaClient:
    return OllamaClient()
