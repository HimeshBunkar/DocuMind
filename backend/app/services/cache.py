from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod

from app.core.config import Settings


class EmbeddingCache(ABC):
    @abstractmethod
    async def get(self, text: str) -> list[float] | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, text: str, embedding: list[float]) -> None:
        raise NotImplementedError


class InMemoryEmbeddingCache(EmbeddingCache):
    def __init__(self) -> None:
        self._cache: dict[str, list[float]] = {}

    async def get(self, text: str) -> list[float] | None:
        return self._cache.get(_key(text))

    async def set(self, text: str, embedding: list[float]) -> None:
        self._cache[_key(text)] = embedding


class RedisEmbeddingCache(EmbeddingCache):
    def __init__(self, settings: Settings) -> None:
        import redis.asyncio as redis

        self.client = redis.from_url(settings.redis_url or "redis://localhost:6379/0")

    async def get(self, text: str) -> list[float] | None:
        value = await self.client.get(_key(text))
        return json.loads(value) if value else None

    async def set(self, text: str, embedding: list[float]) -> None:
        await self.client.set(_key(text), json.dumps(embedding), ex=60 * 60 * 24 * 30)


def _key(text: str) -> str:
    return f"embedding:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def create_embedding_cache(settings: Settings) -> EmbeddingCache:
    if settings.redis_url:
        try:
            return RedisEmbeddingCache(settings)
        except Exception:
            return InMemoryEmbeddingCache()
    return InMemoryEmbeddingCache()
