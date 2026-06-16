"""Educational image generation via Pollinations AI."""

from __future__ import annotations

import urllib.parse

import requests

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.pollinations_base_url

    def generate(self, prompt: str, width: int = 1024, height: int = 768) -> bytes:
        """
        Generate an image from a text prompt using Pollinations AI.
        Returns raw PNG bytes.
        """
        # Append style modifiers for better educational diagrams
        full_prompt = (
            f"{prompt}, educational diagram, clean whiteboard style, "
            "labeled, school textbook illustration, no watermark, high quality"
        )
        encoded = urllib.parse.quote(full_prompt)
        url = f"{self._base_url}/{encoded}?width={width}&height={height}&nologo=true"

        logger.info("Requesting image from Pollinations AI...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise RuntimeError(f"Unexpected content type: {content_type}")
            return response.content
        except requests.RequestException as exc:
            logger.exception("Pollinations AI image request failed")
            raise RuntimeError(f"Image generation failed: {exc}") from exc
