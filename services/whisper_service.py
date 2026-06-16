"""Local Faster-Whisper Speech-to-Text service."""

from __future__ import annotations

import gc
from pathlib import Path

from faster_whisper import WhisperModel
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WhisperService:
    """Local STT using faster-whisper."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model_size = self._settings.whisper_model_size
        self._device = self._settings.whisper_device
        self._compute_type = self._settings.whisper_compute_type
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            logger.info(
                "Loading Faster-Whisper %s on %s (%s)",
                self._model_size,
                self._device,
                self._compute_type,
            )
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )
        return self._model

    def transcribe(self, audio_path: Path) -> tuple[str, str, float]:
        """
        Transcribe audio file.
        Returns: (text, language, probability)
        """
        model = self._get_model()
        
        # Initial prompt to enforce Latin script for Tanglish/Hinglish and prevent hallucination
        initial_prompt = "The following audio may contain Indian code-switched languages like Hinglish or Tanglish. Please write out the transcription exactly as it sounds using English letters (Latin script). For example: Enaku puriyala. Sun is a star."

        segments, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
            initial_prompt=initial_prompt,
        )

        text = " ".join([seg.text for seg in segments]).strip()
        
        # Cleanup memory for CPU
        if self._device == "cpu":
            gc.collect()

        return text, info.language, info.language_probability
