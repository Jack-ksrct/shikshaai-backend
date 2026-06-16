#!/usr/bin/env bash
# ShikshaAI Bharat — Start backend
# Usage: ./start.sh

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "═══════════════════════════════════════════"
echo "  🎓 ShikshaAI Bharat — Startup"
echo "═══════════════════════════════════════════"

# Check .env
if [ ! -f "$ROOT/.env" ]; then
  echo "⚠  .env not found. Copying from .env.example..."
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "📝 Review .env to configure Ollama, then re-run this script."
  exit 1
fi

# Ollama check (optional)
if ! curl -s http://localhost:11434/api/version > /dev/null; then
  echo "⚠  Ollama does not seem to be running at http://localhost:11434"
  echo "   Make sure Ollama is installed and running for AI features to work."
fi

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "❌ ffmpeg is not installed. Run: sudo apt install ffmpeg"
  exit 1
fi

echo ""
echo "▶  Starting FastAPI backend on http://localhost:8000 ..."
cd "$ROOT"
if [ -d "venv" ]; then
  source venv/bin/activate
fi
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"


echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ ShikshaAI Bharat Backend is running!"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "═══════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop the server."

# Wait and cleanup on Ctrl+C
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
