"""Quiz router — /api/quiz"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import QuizRequest, QuizResponse, MCQQuestion, ShortAnswerQuestion, LanguageInfo
from services.quiz_service import QuizService
from services.language_detector import LanguageInfo as DetectorLangInfo
from utils.config import validate_settings
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_service = QuizService()


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


@router.post("/quiz", response_model=QuizResponse)
def generate_quiz(req: QuizRequest):
    errors = validate_settings()
    if errors:
        raise HTTPException(status_code=503, detail=" | ".join(errors))

    try:
        result = _service.generate(
            concept_text=req.concept_text,
            explanation=req.explanation,
            lang_info=_schema_to_detector(req.language_info),
        )
        return QuizResponse(
            mcq_questions=[
                MCQQuestion(
                    question=q.question,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                )
                for q in result.mcq_questions
            ],
            short_answer_questions=[
                ShortAnswerQuestion(
                    question=q.question,
                    model_answer=q.model_answer,
                    keywords=q.keywords,
                )
                for q in result.short_answer_questions
            ],
        )
    except Exception as exc:
        logger.exception("Quiz generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
