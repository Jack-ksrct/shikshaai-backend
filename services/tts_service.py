"""Text-to-Speech service using Microsoft Edge-TTS."""

from __future__ import annotations

import asyncio
import io
import ssl

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Full Indian language → Edge-TTS neural voice map
VOICE_MAP: dict[str, str] = {
    "hindi": "hi-IN-SwaraNeural",
    "hinglish": "hi-IN-SwaraNeural",
    "hi": "hi-IN-SwaraNeural",
    "tamil": "ta-IN-PallaviNeural",
    "tanglish": "ta-IN-PallaviNeural",
    "ta": "ta-IN-PallaviNeural",
    "telugu": "te-IN-ShrutiNeural",
    "te": "te-IN-ShrutiNeural",
    "bengali": "bn-IN-TanishaaNeural",
    "bn": "bn-IN-TanishaaNeural",
    "marathi": "mr-IN-AarohiNeural",
    "mr": "mr-IN-AarohiNeural",
    "gujarati": "gu-IN-DhwaniNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kannada": "kn-IN-SapnaNeural",
    "kn": "kn-IN-SapnaNeural",
    "malayalam": "ml-IN-SobhanaNeural",
    "manglish": "ml-IN-SobhanaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "urdu": "ur-IN-GulNeural",
    "ur": "ur-IN-GulNeural",
    "english": "en-IN-NeerjaNeural",
    "indian english": "en-IN-NeerjaNeural",
    "en": "en-IN-NeerjaNeural",
    "en-in": "en-IN-NeerjaNeural",
}

FALLBACK_VOICE = "hi-IN-SwaraNeural"


class TTSService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def resolve_voice(self, primary_language: str, code_mix_type: str | None = None) -> str:
        """Map a language name / code-mix type to the best Edge-TTS neural voice."""
        # Try code-mix first (e.g. "Hinglish" → Hindi voice)
        for key in [code_mix_type, primary_language]:
            if key:
                voice = VOICE_MAP.get(key.strip().lower())
                if voice:
                    return voice
        return FALLBACK_VOICE

    def _detect_script_voice(self, text: str) -> str | None:
        """Heuristically detect the script of the text to override voice mismatch."""
        counts = {
            "ta-IN-PallaviNeural": sum(1 for c in text if '\u0B80' <= c <= '\u0BFF'),  # Tamil
            "hi-IN-SwaraNeural": sum(1 for c in text if '\u0900' <= c <= '\u097F'),    # Devanagari (Hindi/Marathi)
            "te-IN-ShrutiNeural": sum(1 for c in text if '\u0C00' <= c <= '\u0C7F'),   # Telugu
            "bn-IN-TanishaaNeural": sum(1 for c in text if '\u0980' <= c <= '\u09FF'), # Bengali/Assamese
            "gu-IN-DhwaniNeural": sum(1 for c in text if '\u0A80' <= c <= '\u0AFF'),   # Gujarati
            "kn-IN-SapnaNeural": sum(1 for c in text if '\u0C80' <= c <= '\u0CFF'),    # Kannada
            "ml-IN-SobhanaNeural": sum(1 for c in text if '\u0D00' <= c <= '\u0D7F'),  # Malayalam
            "ur-IN-GulNeural": sum(1 for c in text if '\u0600' <= c <= '\u06FF'),      # Urdu (Arabic Script)
        }
        best_voice = max(counts, key=counts.get)
        if counts[best_voice] > 5:
            return best_voice
        return None

    def synthesize(
        self,
        text: str,
        voice: str | None = None,
        primary_language: str = "Hindi",
        code_mix_type: str | None = None,
    ) -> bytes:
        """Convert text to speech. Returns raw MP3 bytes."""
        if not voice:
            voice = self.resolve_voice(primary_language, code_mix_type)

        # Safety fallback: if the actual text is in a different script than the detected voice
        script_voice = self._detect_script_voice(text)
        if script_voice:
            voice = script_voice

        import re
        # Remove markdown characters
        text = re.sub(r'[*#_~`]', '', text)
        # Remove emojis (Supplementary planes and Miscellaneous Symbols)
        text = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf]', '', text)
        
        # Truncate very long text
        if len(text) > 2000:
            text = text[:2000] + "..."

        logger.info("TTS: voice=%s len=%d", voice, len(text))

        try:
            return asyncio.run(self._async_synthesize(text, voice))
        except RuntimeError:
            # Already inside an event loop — run in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, self._async_synthesize(text, voice))
                return future.result(timeout=60)

    @staticmethod
    async def _async_synthesize(text: str, voice: str) -> bytes:
        import edge_tts  # type: ignore

        # Create a permissive SSL context to handle corporate/dev proxies
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        communicate = edge_tts.Communicate(text, voice)
        buf = io.BytesIO()

        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
        except Exception as exc:
            # Try once more with default SSL (works on most production servers)
            logger.warning("TTS stream error (ssl_ctx): %s — retrying with default SSL", exc)
            communicate2 = edge_tts.Communicate(text, voice)
            buf = io.BytesIO()
            async for chunk in communicate2.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])

        data = buf.getvalue()
        if not data:
            raise RuntimeError(f"Edge-TTS returned empty audio for voice '{voice}'")
        return data
