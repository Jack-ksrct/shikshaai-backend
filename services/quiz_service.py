"""Quiz generation service."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from services.ollama_client import get_ollama_client
from services.language_detector import LanguageInfo
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MCQQuestion:
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


@dataclass
class ShortAnswerQuestion:
    question: str
    model_answer: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class QuizResult:
    mcq_questions: list[MCQQuestion]
    short_answer_questions: list[ShortAnswerQuestion]


_QUIZ_PROMPT = """You are ShikshaAI Bharat, generating a quiz for students.

Concept Request: {concept}
Explanation: {explanation}
Target Language: {language}
Code-mix style: {code_mix}

Generate a quiz as valid JSON only (no markdown, no backticks).
Follow the user's Concept Request for the number and type of questions (e.g., if they ask for "10 MCQs", generate 10 MCQs and 0 short-answer questions). If no number is specified, default to 3 MCQs and 2 short-answer questions.
CRITICAL: You MUST write the entire quiz in the exact Target Language specified above. Do NOT use Hindi unless the Target Language is Hindi.

{{
  "mcq_questions": [
    {{
      "question": "<question in Target Language>",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "explanation": "<why this is correct, in Target Language>"
    }}
  ],
  "short_answer_questions": [
    {{
      "question": "<question in Target Language>",
      "model_answer": "<expected answer in Target Language>",
      "keywords": ["<keyword1>", "<keyword2>"]
    }}
  ]
}}
"""


class QuizService:
    def __init__(self) -> None:
        self._client = get_ollama_client()

    def generate(self, concept_text: str, explanation: str, lang_info: LanguageInfo) -> QuizResult:
        prompt = _QUIZ_PROMPT.format(
            concept=concept_text[:300],
            explanation=explanation[:500],
            language=lang_info.primary_language,
            code_mix=lang_info.code_mix_type or "none",
        )
        try:
            raw = self._client.generate(prompt)
            # Strip markdown code fences if present
            raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
            # Find the JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON object in Gemini quiz response")
            data = json.loads(match.group())

            mcqs = [
                MCQQuestion(
                    question=q.get("question", ""),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", "A"),
                    explanation=q.get("explanation", ""),
                )
                for q in data.get("mcq_questions", [])
            ]
            sas = [
                ShortAnswerQuestion(
                    question=q.get("question", ""),
                    model_answer=q.get("model_answer", ""),
                    keywords=q.get("keywords", []),
                )
                for q in data.get("short_answer_questions", [])
            ]
            return QuizResult(mcq_questions=mcqs, short_answer_questions=sas)

        except Exception as exc:
            logger.exception("Quiz generation failed")
            raise RuntimeError(f"Quiz generation failed: {exc}") from exc
