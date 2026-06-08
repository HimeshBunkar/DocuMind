from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    id: str
    name: str
    file_type: str
    status: Literal["queued", "processing", "ready", "failed"]
    chunk_count: int = 0
    page_count: int = 0
    uploaded_at: datetime
    summary: str | None = None


class Chunk(BaseModel):
    id: str
    document_id: str
    document_name: str
    text: str
    page: int
    paragraph: int
    embedding: list[float] = Field(default_factory=list)


class Citation(BaseModel):
    document_id: str
    document_name: str
    page: int
    paragraph: int
    text: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)
    mode: Literal["single", "compare"] = "single"
    top_k: int = Field(default=5, ge=1, le=12)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: int
    provider: str


class StreamEvent(BaseModel):
    type: Literal["token", "citations", "done", "error"]
    value: str | list[Citation] | None = None


class UploadResponse(BaseModel):
    document: DocumentMeta
    chunks_preview: list[Citation]


class DeleteResponse(BaseModel):
    deleted: bool
    document_id: str
