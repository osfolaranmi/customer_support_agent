from pathlib import Path
import os

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BACKEND_DIR / ".env"
KNOWLEDGEBASE_DIR = BACKEND_DIR / "knowledgebase"
VECTOR_STORE_DIR = BACKEND_DIR / "vector_store"

load_dotenv(ENV_FILE)

#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")