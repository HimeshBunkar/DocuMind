from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = "DocuMind API"
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    embedding_provider: Literal["local", "openai", "huggingface", "gemini"] = "gemini"
    llm_provider: Literal["local", "openai", "gemini", "groq"] = "groq"
    vector_store: Literal["memory", "chroma", "pinecone"] = "memory"

    # OpenAI (optional)
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o"

    # HuggingFace (optional)
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Google Gemini (embeddings)
    gemini_api_key: str | None = None
    gemini_chat_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    # Groq (free LLM)
    groq_api_key: str | None = None
    groq_chat_model: str = "llama-3.3-70b-versatile"

    # Optional services
    pinecone_api_key: str | None = None
    pinecone_index: str | None = None
    redis_url: str | None = None
    mongodb_uri: str | None = None

    chunk_size: int = 950
    chunk_overlap: int = 160
    top_k: int = 5
    storage_dir: str = "storage"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()