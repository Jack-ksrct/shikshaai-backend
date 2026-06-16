"""Explain router — /api/explain"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import ExplainRequest, ExplainResponse, LanguageInfo
from services.concept_service import ConceptService
from services.language_detector import LanguageInfo as DetectorLangInfo
from utils.config import validate_settings
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_service = ConceptService()


def _schema_to_detector(li: LanguageInfo) -> DetectorLangInfo:
    return DetectorLangInfo(
        primary_language=li.primary_language,
        secondary_languages=li.secondary_languages,
        code_mix_type=li.code_mix_type,
        script=li.script,
        confidence=li.confidence,
        language_style_note=li.language_style_note,
        display_label=li.display_label,
    )


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    errors = validate_settings()
    if errors:
        raise HTTPException(status_code=503, detail=" | ".join(errors))

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Concept text cannot be empty.")

    try:
        explanation = _service.simplify(
            text=req.text,
            lang_info=_schema_to_detector(req.language_info),
            grade_level=req.grade_level,
        )
        return ExplainResponse(explanation=explanation, topic=req.text[:100])
    except Exception as exc:
        logger.exception("Explanation generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
