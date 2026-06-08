from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.models.schemas import Citation, Chunk, DocumentMeta, QueryResponse
from app.services.cache import EmbeddingCache
from app.services.chunker import RecursiveChunker
from app.services.document_store import DocumentStore
from app.services.embeddings import EmbeddingProvider
from app.services.llm import ResponseSynthesizer
from app.services.text_extractor import extract_paragraphs
from app.services.vector_store import VectorStore


class RagService:
    def __init__(
        self,
        settings: Settings,
        documents: DocumentStore,
        embeddings: EmbeddingProvider,
        cache: EmbeddingCache,
        vectors: VectorStore,
        synthesizer: ResponseSynthesizer
    ) -> None:
        self.settings = settings
        self.documents = documents
        self.embeddings = embeddings
        self.cache = cache
        self.vectors = vectors
        self.synthesizer = synthesizer
        self.chunker = RecursiveChunker(settings.chunk_size, settings.chunk_overlap)

    async def ingest(self, filename: str, content_type: str | None, content: bytes) -> tuple[DocumentMeta, list[Citation]]:
        file_type = content_type or Path(filename).suffix.lstrip(".") or "document"
        document = self.documents.create(filename, file_type)
        paragraphs, page_count = extract_paragraphs(filename, content)
        chunked = self.chunker.split(paragraphs)

        chunks: list[Chunk] = []
        for item in chunked:
            chunks.append(
                Chunk(
                    id=str(uuid4()),
                    document_id=document.id,
                    document_name=document.name,
                    text=item.text,
                    page=item.page,
                    paragraph=item.paragraph
                )
            )

        await self._embed_chunks(chunks)
        await self.vectors.upsert(chunks)

        document.status = "ready"
        document.chunk_count = len(chunks)
        document.page_count = page_count
        document.summary = _summarize([chunk.text for chunk in chunks])
        self.documents.update(document)

        preview = [
            Citation(
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                page=chunk.page,
                paragraph=chunk.paragraph,
                text=chunk.text,
                score=1.0
            )
            for chunk in chunks[:3]
        ]
        return document, preview

    async def query(self, question: str, document_ids: list[str], top_k: int, compare: bool = False) -> QueryResponse:
        started = time.perf_counter()
        query_embedding = (await self.embeddings.embed([question]))[0]
        matches = await self.vectors.search(query_embedding, document_ids, top_k)
        citations = [
            Citation(
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                page=chunk.page,
                paragraph=chunk.paragraph,
                text=chunk.text,
                score=round(score, 4)
            )
            for chunk, score in matches
        ]
        answer = await self.synthesizer.answer(question, citations, compare=compare)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return QueryResponse(
            answer=answer,
            citations=citations,
            latency_ms=elapsed_ms,
            provider=self.embeddings.name
        )

    async def delete_document(self, document_id: str) -> bool:
        deleted = self.documents.delete(document_id)
        await self.vectors.delete_document(document_id)
        return deleted

    async def _embed_chunks(self, chunks: list[Chunk]) -> None:
        uncached: list[Chunk] = []
        for chunk in chunks:
            cached = await self.cache.get(chunk.text)
            if cached:
                chunk.embedding = cached
            else:
                uncached.append(chunk)

        if not uncached:
            return

        embeddings = await self.embeddings.embed([chunk.text for chunk in uncached])
        for chunk, embedding in zip(uncached, embeddings, strict=True):
            chunk.embedding = embedding
            await self.cache.set(chunk.text, embedding)


def _summarize(texts: list[str]) -> str:
    joined = " ".join(texts).strip()
    if len(joined) <= 180:
        return joined
    return f"{joined[:177].rstrip()}..."
