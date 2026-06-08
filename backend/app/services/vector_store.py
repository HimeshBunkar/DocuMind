from __future__ import annotations

import math
from abc import ABC, abstractmethod

from app.core.config import Settings
from app.models.schemas import Chunk


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks: list[Chunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(self, embedding: list[float], document_ids: list[str], top_k: int) -> list[tuple[Chunk, float]]:
        raise NotImplementedError

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}

    async def upsert(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    async def search(self, embedding: list[float], document_ids: list[str], top_k: int) -> list[tuple[Chunk, float]]:
        allowed = set(document_ids)
        matches: list[tuple[Chunk, float]] = []
        for chunk in self._chunks.values():
            if allowed and chunk.document_id not in allowed:
                continue
            score = cosine_similarity(embedding, chunk.embedding)
            matches.append((chunk, score))
        matches.sort(key=lambda item: item[1], reverse=True)
        return matches[:top_k]

    async def delete_document(self, document_id: str) -> None:
        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if chunk.document_id != document_id
        }


class ChromaVectorStore(VectorStore):
    def __init__(self, settings: Settings) -> None:
        import chromadb

        client = chromadb.PersistentClient(path=f"{settings.storage_dir}/chroma")
        self.collection = client.get_or_create_collection(
            name="documind_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    async def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=[chunk.embedding for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "page": chunk.page,
                    "paragraph": chunk.paragraph
                }
                for chunk in chunks
            ]
        )

    async def search(self, embedding: list[float], document_ids: list[str], top_k: int) -> list[tuple[Chunk, float]]:
        where = {"document_id": {"$in": document_ids}} if document_ids else None
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where
        )
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: list[tuple[Chunk, float]] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            chunk = Chunk(
                id=chunk_id,
                document_id=str(metadata["document_id"]),
                document_name=str(metadata["document_name"]),
                page=int(metadata["page"]),
                paragraph=int(metadata["paragraph"]),
                text=text,
                embedding=[]
            )
            matches.append((chunk, max(0.0, min(1.0, 1.0 - float(distance)))))
        return matches

    async def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})


class PineconeVectorStore(VectorStore):
    def __init__(self, settings: Settings) -> None:
        if not settings.pinecone_api_key or not settings.pinecone_index:
            raise ValueError("Pinecone requires PINECONE_API_KEY and PINECONE_INDEX.")

        from pinecone import Pinecone

        self.index = Pinecone(api_key=settings.pinecone_api_key).Index(settings.pinecone_index)

    async def upsert(self, chunks: list[Chunk]) -> None:
        vectors = [
            {
                "id": chunk.id,
                "values": chunk.embedding,
                "metadata": {
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "page": chunk.page,
                    "paragraph": chunk.paragraph,
                    "text": chunk.text
                }
            }
            for chunk in chunks
        ]
        if vectors:
            self.index.upsert(vectors=vectors)

    async def search(self, embedding: list[float], document_ids: list[str], top_k: int) -> list[tuple[Chunk, float]]:
        pinecone_filter = {"document_id": {"$in": document_ids}} if document_ids else None
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=pinecone_filter
        )
        matches: list[tuple[Chunk, float]] = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            chunk = Chunk(
                id=match["id"],
                document_id=str(metadata["document_id"]),
                document_name=str(metadata["document_name"]),
                page=int(metadata["page"]),
                paragraph=int(metadata["paragraph"]),
                text=str(metadata["text"]),
                embedding=[]
            )
            matches.append((chunk, float(match.get("score", 0.0))))
        return matches

    async def delete_document(self, document_id: str) -> None:
        self.index.delete(filter={"document_id": document_id})


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    width = min(len(left), len(right))
    dot = sum(left[index] * right[index] for index in range(width))
    left_norm = math.sqrt(sum(value * value for value in left[:width])) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right[:width])) or 1.0
    return max(0.0, min(1.0, (dot / (left_norm * right_norm) + 1) / 2))


def create_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_store == "chroma":
        try:
            return ChromaVectorStore(settings)
        except Exception:
            return InMemoryVectorStore()
    if settings.vector_store == "pinecone":
        try:
            return PineconeVectorStore(settings)
        except Exception:
            return InMemoryVectorStore()
    return InMemoryVectorStore()
