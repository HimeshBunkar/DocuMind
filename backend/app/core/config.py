from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuMind API"
    app_env: str = "development"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    embedding_provider: Literal[
        "local",
        "openai",
        "huggingface"
    ] = "local"

    llm_provider: Literal[
        "local",
        "openai",
        "huggingface",
        "gemini"
    ] = "local"

    vector_store: Literal[
        "memory",
        "chroma",
        "pinecone"
    ] = "memory"

    # OpenAI
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o"

    # Gemini
    gemini_api_key: str | None = None
    gemini_chat_model: str = "gemini-2.5-flash"

    # HuggingFace
    huggingface_embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_index: str | None = None

    # Optional Services
    redis_url: str | None = None
    mongodb_uri: str | None = None

    # RAG Settings
    chunk_size: int = 950
    chunk_overlap: int = 160
    top_k: int = 5

    # Storage
    storage_dir: str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()