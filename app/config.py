from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_DIR = ROOT / "vectorstore"
DB_DIR = ROOT / "database"
CONFIG_DIR = ROOT / "config"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K", "5"))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.0"))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
for p in [DATA_DIR, DOCS_DIR, PROCESSED_DIR, VECTOR_DIR, DB_DIR]: p.mkdir(parents=True, exist_ok=True)
