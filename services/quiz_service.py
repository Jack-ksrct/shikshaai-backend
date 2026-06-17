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
CRITICAL REQUIREMENT: You MUST generate EXACTLY {mcq_count} MCQ questions in the "mcq_questions" array. Do NOT generate more or less.
Generate EXACTLY 2 short-answer questions.
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
        # Extract requested number of MCQs from concept text
        import re
        match = re.search(r'\b(\d+)\s*(?:mcq|question|qn)s?\b', concept_text.lower())
        mcq_count = int(match.group(1)) if match else 3
        # Cap at 25 to prevent memory/timeout issues
        mcq_count = min(mcq_count, 25)

        prompt = _QUIZ_PROMPT.format(
            concept=concept_text[:300],
            explanation=explanation[:500],
            language=lang_info.primary_language,
            code_mix=lang_info.code_mix_type or "none",
            mcq_count=mcq_count
        )
        try:
            raw = self._client.generate(prompt, format="json")
            # Strip markdown code fences if present
            raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
            # Find the JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON object in Gemini quiz response")
            data = json.loads(match.group())

            mcqs = []
            for q in data.get("mcq_questions", []):
                if isinstance(q, dict):
                    mcqs.append(MCQQuestion(
                        question=q.get("question", ""),
                        options=q.get("options", []) if isinstance(q.get("options"), list) else [],
                        correct_answer=q.get("correct_answer", "A"),
                        explanation=q.get("explanation", ""),
                    ))

            sas = []
            for q in data.get("short_answer_questions", []):
                if isinstance(q, dict):
                    sas.append(ShortAnswerQuestion(
                        question=q.get("question", ""),
                        model_answer=q.get("model_answer", ""),
                        keywords=q.get("keywords", []) if isinstance(q.get("keywords"), list) else [],
                    ))

            return QuizResult(mcq_questions=mcqs, short_answer_questions=sas)

        except Exception as exc:
            logger.exception("Quiz generation failed")
            raise RuntimeError(f"Quiz generation failed: {exc}") from exc
