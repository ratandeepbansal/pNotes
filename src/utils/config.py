"""Configuration settings for the RAG system."""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Notes directory
NOTES_DIR = PROJECT_ROOT / "notes"

# Database files
DB_DIR = PROJECT_ROOT / "data"
SQLITE_DB_PATH = DB_DIR / "metadata.db"
CHROMA_DB_PATH = DB_DIR / "chroma"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Retrieval settings
TOP_K_RESULTS = 5

def ensure_directories():
    """Ensure all required directories exist."""
    DB_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)
