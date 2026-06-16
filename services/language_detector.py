"""Language detection service — identifies Indian languages and code-mixing."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from utils.logger import get_logger

logger = get_logger(__name__)

# ISO-639-1 → display name map for Indian languages
LANG_DISPLAY = {
    "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ur": "Urdu",
    "sa": "Sanskrit", "ne": "Nepali", "sd": "Sindhi",
    "en": "English", "mixed": "Code-Mixed",
}

WHISPER_TO_DISPLAY = {
    **LANG_DISPLAY,
    "unknown": "Unknown",
}

SCRIPT_MAP = {
    "hi": "Devanagari", "mr": "Devanagari", "ne": "Devanagari",
    "sa": "Devanagari", "ur": "Nastaliq",
    "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "bn": "Bengali", "as": "Bengali",
    "gu": "Gujarati", "pa": "Gurmukhi", "or": "Odia",
    "en": "Latin",
}


@dataclass
class LanguageInfo:
    primary_language: str = "English"
    secondary_languages: list[str] = field(default_factory=list)
    code_mix_type: str | None = None
    script: str = "Latin"
    confidence: float = 0.9
    language_style_note: str = ""
    display_label: str = ""

    def __post_init__(self) -> None:
        if not self.display_label:
            self.display_label = self.primary_language


class LanguageDetector:
    """Two-stage language detector: Whisper → Ollama confirmation."""

    _PROMPT = """You are a linguist specializing in Indian languages and code-mixing.
Analyze the following text and return a JSON object (no markdown, no backticks):

{{
  "primary_language": "<full language name, e.g. Hindi, Tamil, Hinglish>",
  "secondary_languages": ["<other languages present>"],
  "code_mix_type": "<e.g. Hinglish, Tanglish, or null if pure>",
  "script": "<Devanagari | Latin | Tamil | Telugu | Kannada | Malayalam | Bengali | Gujarati | Gurmukhi | Odia | Mixed>",
  "confidence": <0.0-1.0>,
  "language_style_note": "<one sentence about how the student is communicating>",
  "display_label": "<short label for UI, e.g. 'Hindi', 'Hinglish', 'Tamil'>"
}}

Text to analyze:
\"\"\"{text}\"\"\"

Whisper detected language: {whisper_lang}
"""

    def __init__(self) -> None:
        self._client: object | None = None

    def _get_client(self):
        if self._client is None:
            from services.ollama_client import get_ollama_client
            self._client = get_ollama_client()
        return self._client

    def _whisper_to_info(self, lang_code: str, prob: float) -> LanguageInfo:
        """Build a LanguageInfo from a Whisper language code."""
        display = WHISPER_TO_DISPLAY.get(lang_code, lang_code.title())
        script = SCRIPT_MAP.get(lang_code, "Latin")
        return LanguageInfo(
            primary_language=display,
            secondary_languages=[],
            code_mix_type=None,
            script=script,
            confidence=prob,
            language_style_note=f"Student is communicating in {display}.",
            display_label=display,
        )

    def detect(self, text: str, whisper_lang: str | None = None, whisper_prob: float = 0.0) -> LanguageInfo:
        """
        Detect language of text. Uses Ollama for rich code-mix detection.
        Falls back gracefully if Ollama fails.
        """
        if not text.strip():
            return LanguageInfo()

        try:
            client = self._get_client()
            prompt = self._PROMPT.format(
                text=text[:500],
                whisper_lang=whisper_lang or "unknown",
            )
            raw = client.generate(prompt)
            # Extract JSON from response
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON in Ollama response")
            data = json.loads(match.group())
            return LanguageInfo(
                primary_language=data.get("primary_language", "English"),
                secondary_languages=data.get("secondary_languages", []),
                code_mix_type=data.get("code_mix_type"),
                script=data.get("script", "Latin"),
                confidence=float(data.get("confidence", 0.85)),
                language_style_note=data.get("language_style_note", ""),
                display_label=data.get("display_label", data.get("primary_language", "English")),
            )
        except Exception as exc:
            logger.warning("Ollama language detection failed: %s — using Whisper fallback.", exc)
            if whisper_lang and whisper_lang not in ("", "unknown"):
                return self._whisper_to_info(whisper_lang, whisper_prob or 0.75)
            return LanguageInfo()
