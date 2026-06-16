"""STT router — /api/transcribe and /api/detect-language"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.schemas import TranscribeResponse, LanguageInfo, DetectLanguageRequest
from services.whisper_service import WhisperService
from services.language_detector import LanguageDetector
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

_stt = WhisperService()
_detector = LanguageDetector()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    grade_level: str = Form("Class 6-8"),
):
    """Transcribe uploaded audio locally and detect language."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file received.")

    # Write to temp file for Whisper STT
    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = Path(tmp.name)

    try:
        text, lang, prob = _stt.transcribe(tmp_path)
        lang_info = _detector.detect(text, whisper_lang=lang, whisper_prob=prob)
        
        result = {
            "text": text,
            "language": lang,
            "language_probability": prob,
            "language_info": lang_info.__dict__,
        }
    except Exception as exc:
        logger.exception("STT transcription failed")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")
    finally:
        tmp_path.unlink(missing_ok=True)

    return TranscribeResponse(**result)


@router.post("/detect-language", response_model=LanguageInfo)
def detect_language(req: DetectLanguageRequest):
    """Detect language of plain text (no audio)."""
    try:
        info = _detector.detect(req.text, whisper_lang=req.whisper_lang)
        return LanguageInfo(**info.__dict__)
    except Exception as exc:
        logger.exception("Language detection error")
        raise HTTPException(status_code=500, detail=str(exc))
