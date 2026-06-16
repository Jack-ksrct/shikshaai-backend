"""Pydantic schemas for ShikshaAI Bharat API."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class LanguageInfo(BaseModel):
    primary_language: str = "English"
    secondary_languages: list[str] = []
    code_mix_type: Optional[str] = None
    script: str = "Latin"
    confidence: float = 0.9
    language_style_note: str = ""
    display_label: str = ""


# ── Transcribe ──────────────────────────────────────────────────────────────
class TranscribeResponse(BaseModel):
    text: str
    language: str
    language_probability: float
    language_info: LanguageInfo


# ── Detect language (text-only) ──────────────────────────────────────────────
class DetectLanguageRequest(BaseModel):
    text: str
    whisper_lang: Optional[str] = None


# ── Explain ──────────────────────────────────────────────────────────────────
class ExplainRequest(BaseModel):
    text: str
    language_info: LanguageInfo
    grade_level: str = "Class 6-8"


class ExplainResponse(BaseModel):
    explanation: str
    topic: str


# ── Quiz ─────────────────────────────────────────────────────────────────────
class QuizRequest(BaseModel):
    concept_text: str
    explanation: str
    language_info: LanguageInfo


class MCQQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


class ShortAnswerQuestion(BaseModel):
    question: str
    model_answer: str
    keywords: list[str] = []


class QuizResponse(BaseModel):
    mcq_questions: list[MCQQuestion]
    short_answer_questions: list[ShortAnswerQuestion]


# ── Visual ────────────────────────────────────────────────────────────────────
class VisualRequest(BaseModel):
    concept_text: str
    explanation: str


class VisualResponse(BaseModel):
    image_base64: str
    prompt: str


# ── TTS ───────────────────────────────────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str
    primary_language: str = "Hindi"
    code_mix_type: Optional[str] = None


class TTSResponse(BaseModel):
    audio_base64: str
    voice: str
