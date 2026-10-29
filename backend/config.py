"""
Configuration settings for VeritasAI Fake News Detector.
Loads environment variables from .env file with secure fallbacks.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

# Load .env file from project root
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# API Keys & LLM Provider Settings
# Supported providers: 'freellmapi', 'gemini', 'openai_compatible'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "freellmapi").strip().lower()
LLM_API_KEY = (os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.freellmapi.com/v1").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b").strip()

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or LLM_API_KEY).strip()

# Server Settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Model Configuration
BERT_MODEL_NAME = os.getenv("BERT_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
USE_FALLBACK_CLASSIFIER = os.getenv("USE_FALLBACK_CLASSIFIER", "True").lower() in ("true", "1", "yes")

# Database Path
DB_PATH = DATA_DIR / "veritas_history.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

