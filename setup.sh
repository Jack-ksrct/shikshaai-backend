#!/usr/bin/env bash
# ShikshaAI Bharat — Setup Script
# Usage: chmod +x setup.sh && ./setup.sh

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "═══════════════════════════════════════════"
echo "  🎓 ShikshaAI Bharat — Setup"
echo "═══════════════════════════════════════════"
echo ""

# ── System dependencies ──────────────────────────────────────────────────────
echo "[1/4] Checking system dependencies..."

if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3.10+ is required. Install from https://python.org"
  exit 1
fi
echo "  ✓ Python: $(python3 --version)"

if ! command -v ffmpeg &>/dev/null; then
  echo "  Installing ffmpeg..."
  if command -v apt-get &>/dev/null; then
    sudo apt-get install -y ffmpeg
  elif command -v brew &>/dev/null; then
    brew install ffmpeg
  else
    echo "  ⚠  Please install ffmpeg manually: https://ffmpeg.org/download.html"
  fi
fi
echo "  ✓ ffmpeg: $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"


# ── Python virtual environment ───────────────────────────────────────────────
echo ""
echo "[2/4] Setting up Python virtual environment..."
cd "$ROOT"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip -q
pip install -r backend/requirements.txt

echo "  ✓ Python packages installed"

# ── Pre-download Whisper model ───────────────────────────────────────────────
echo ""
echo "[3/4] Pre-downloading Whisper base model (~145MB)..."
python3 -c "
from faster_whisper import WhisperModel
print('  Downloading model...')
WhisperModel('base', device='cpu', compute_type='int8')
print('  ✓ Whisper model ready')
"


# ── .env setup ───────────────────────────────────────────────────────────────
cd "$ROOT"
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  ⚠  ACTION REQUIRED:"
  echo "  Ensure Ollama is installed and running."
  echo "  Download Ollama: https://ollama.com"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Ensure Ollama is running locally"
echo "  2. Run: chmod +x start.sh && ./start.sh"
echo "═══════════════════════════════════════════"
