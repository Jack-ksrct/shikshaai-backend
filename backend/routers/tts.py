"""TTS router — /api/tts"""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException

from backend.schemas import TTSRequest, TTSResponse
from services.tts_service import TTSService
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_service = TTSService()


@router.post("/tts", response_model=TTSResponse)
def text_to_speech(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    voice = _service.resolve_voice(req.primary_language, req.code_mix_type)
    try:
        audio_bytes = _service.synthesize(
            text=req.text,
            voice=voice,
            primary_language=req.primary_language,
            code_mix_type=req.code_mix_type,
        )
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return TTSResponse(audio_base64=audio_b64, voice=voice)
    except Exception as exc:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail=f"TTS failed: {exc}")
