"""ShikshaAI Bharat — FastAPI Backend"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.config import validate_settings, get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="ShikshaAI Bharat API",
    description="Voice-Powered Multilingual Classroom Copilot for Indian Schools",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
def health():
    cfg_errors = validate_settings()
    s = get_settings()
    return {
        "status": "ok",
        "config_errors": cfg_errors,
        "ollama_model": s.ollama_model,
        "whisper_model": s.whisper_model_size,
        "whisper_device": s.whisper_device,
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": "ShikshaAI Bharat API v2.0", "docs": "/docs", "health": "/api/health"}


# ── Include routers AFTER app is defined ──────────────────────────────────────
from backend.routers import transcribe, explain, quiz, visual, tts  # noqa: E402

app.include_router(transcribe.router, prefix="/api", tags=["STT"])
app.include_router(explain.router,    prefix="/api", tags=["Explain"])
app.include_router(quiz.router,       prefix="/api", tags=["Quiz"])
app.include_router(visual.router,     prefix="/api", tags=["Visual"])
app.include_router(tts.router,        prefix="/api", tags=["TTS"])
