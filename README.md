# ShikshaAI Bharat - Backend

This is the backend repository for **ShikshaAI Bharat**, a multilingual, voice-first educational platform designed for Indian students. It acts as an intelligent classroom copilot that can explain concepts, generate educational diagrams, create quizzes, and transcribe speech in real-time.

This backend is built for performance and runs entirely independently, featuring local AI capabilities to bypass expensive API costs.

## Core Architecture & Features

- **FastAPI Core**: High-performance, async Python web framework.
- **Local LLM Inference**: Powered by local [Ollama](https://ollama.ai/) models (`qwen2.5:1.5b` recommended for CPU efficiency) for fast, free text generation (Explanations, Quizzes).
- **Speech-to-Text**: Utilizes `Faster-Whisper` for fast, offline audio transcription and language detection.
- **Text-to-Speech**: Integrates with `Edge-TTS` to provide natural-sounding voice explanations.
- **Image Generation**: Uses `Pollinations AI` to automatically generate relevant classroom diagrams and visuals.
- **Ngrok Tunneling**: Includes automated logic to securely expose the local backend to the internet via Ngrok, allowing the frontend to connect dynamically.

## Project Structure

```
├── backend/            # FastAPI routers and main application logic
├── services/           # Core AI service integrations
│   ├── ollama_client.py   # Interfaces with local Ollama models
│   ├── concept_service.py # Generates simplified explanations
│   ├── quiz_service.py    # Generates dynamic MCQs and short answers
│   ├── tts_service.py     # Text-to-Speech processing
│   ├── stt_service.py     # Speech-to-Text (Whisper) handling
│   └── visual_service.py  # Image prompt generation & fetching
├── utils/              # Configuration, logging, and helpers
├── setup.sh            # Automated installation of dependencies & models
├── start.sh            # Production script to launch FastAPI and Ngrok
└── .env.example        # Template for environment variables
```

## Prerequisites

To run this backend, you will need:
- Linux / Ubuntu OS (Tested on Google Cloud Platform)
- Python 3.10+
- [Ollama](https://ollama.ai/) installed locally
- Ngrok account (for tunneling)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Jack-ksrct/shikshaai-backend.git
   cd shikshaai-backend
   ```

2. **Run the setup script:**
   This script will automatically create a Python virtual environment, install all required dependencies (FastAPI, Whisper, etc.), and download the necessary Ollama models.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Environment Variables:**
   Copy the example environment file and update it with your settings.
   ```bash
   cp .env.example .env
   nano .env
   ```
   **Important Settings:**
   * `OLLAMA_MODEL=qwen2.5:1.5b` (Recommended for fast CPU inference)
   * `OLLAMA_BASE_URL=http://localhost:11434`

4. **Start the Server:**
   The start script will launch the FastAPI server and automatically spin up an Ngrok tunnel so your frontend can connect to it.
   ```bash
   ./start.sh
   ```

## Development & Maintenance

* **Model Troubleshooting:** If quiz generation fails with JSON errors, the backend is equipped with a robust JSON parser that forces strict structural formatting. Ensure you are using `qwen2.5:1.5b` or a larger model for the best formatting adherence.
* **Port Conflicts:** If you encounter an `[Errno 98] Address already in use` error when starting, use `pkill -f uvicorn` or `sudo fuser -k 8000/tcp` to terminate ghost processes.

## License
MIT License
