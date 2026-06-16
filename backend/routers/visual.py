"""Visual router — /api/visual"""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException

from backend.schemas import VisualRequest, VisualResponse
from services.image_service import ImageService
from services.concept_service import ConceptService
from utils.config import validate_settings
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
_image_svc = ImageService()
_concept_svc = ConceptService()


@router.post("/visual", response_model=VisualResponse)
def generate_visual(req: VisualRequest):
    errors = validate_settings()
    if errors:
        raise HTTPException(status_code=503, detail=" | ".join(errors))

    try:
        # Step 1: Ollama optimises the image prompt
        img_prompt = _concept_svc.build_diagram_prompt(req.concept_text, req.explanation)
        # Step 2: Generate image from Pollinations
        img_bytes = _image_svc.generate(img_prompt)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return VisualResponse(image_base64=img_b64, prompt=img_prompt)
    except Exception as exc:
        logger.exception("Visual generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
