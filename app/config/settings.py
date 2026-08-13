import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# LOAD .ENV
# =========================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


# =========================================================
# SETTINGS
# =========================================================

class Settings:

    # =====================================================
    # GEMINI
    # =====================================================

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )


    # =====================================================
    # MISTRAL
    # =====================================================

    MISTRAL_API_KEY: str = os.getenv(
        "MISTRAL_API_KEY",
        ""
    )

    MISTRAL_MODEL: str = os.getenv(
        "MISTRAL_MODEL",
        "mistral-small-latest"
    )


    # =====================================================
    # PINECONE
    # =====================================================

    PINECONE_API_KEY: str = os.getenv(
        "PINECONE_API_KEY",
        ""
    )

    PINECONE_INDEX_NAME: str = os.getenv(
        "PINECONE_INDEX_NAME",
        ""
    )


    # =====================================================
    # EMBEDDINGS
    # =====================================================

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )


    # =====================================================
    # APPLICATION
    # =====================================================

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Agentic RAG Assistant"
    )

    DEBUG: bool = os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"


# =========================================================
# SINGLE SETTINGS INSTANCE
# =========================================================

settings = Settings()