from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

from app.core.config import Settings


class EmbeddingProvider(ABC):
    name: str

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    name = "local-hash-embedding"

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def embed(self, texts: list[str]) -> list[list[float]]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        response = await client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    name = "huggingface"

    def __init__(self, settings: Settings) -> None:
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(settings.huggingface_embedding_model)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]


class GeminiEmbeddingProvider(EmbeddingProvider):
    name = "gemini"

    def __init__(self, settings: Settings) -> None:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = settings.gemini_embedding_model
        # Always ensure models/ prefix
        if not model.startswith("models/") and not model.startswith("tunedModels/"):
            model = f"models/{model}"
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import asyncio
        import google.generativeai as genai

        loop = asyncio.get_event_loop()

        def _embed_batch() -> list[list[float]]:
            results = []
            for text in texts:
                response = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                results.append(response["embedding"])
            return results

        return await loop.run_in_executor(None, _embed_batch)


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "gemini" and settings.gemini_api_key:
        try:
            return GeminiEmbeddingProvider(settings)
        except Exception:
            return LocalEmbeddingProvider()
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider(settings)
    if settings.embedding_provider == "huggingface":
        try:
            return HuggingFaceEmbeddingProvider(settings)
        except Exception:
            return LocalEmbeddingProvider()
    return LocalEmbeddingProvider()