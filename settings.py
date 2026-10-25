"""Local configuration for Chapter 16."""
from pathlib import Path

MODEL = "qwen3.5:9b"
OLLAMA_HOST = "http://localhost:11434"
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "data" / "office_policies.json"
OUTPUT_DIR = BASE_DIR / "output"
MAX_TASK_LENGTH = 400
MAX_QUEUE = 10
