from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.models.schemas import DeleteResponse, QueryRequest, StreamEvent, UploadResponse
from app.services.cache import create_embedding_cache
from app.services.document_store import DocumentStore
from app.services.embeddings import create_embedding_provider
from app.services.llm import ResponseSynthesizer
from app.services.rag import RagService
from app.services.vector_store import create_vector_store

settings = get_settings()
documents = DocumentStore(settings)
embedding_provider = create_embedding_provider(settings)
embedding_cache = create_embedding_cache(settings)
vector_store = create_vector_store(settings)
synthesizer = ResponseSynthesizer(settings)
rag = RagService(settings, documents, embedding_provider, embedding_cache, vector_store, synthesizer)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "embedding_provider": embedding_provider.name,
        "vector_store": settings.vector_store
    }


@app.get("/documents")
async def list_documents():
    return documents.list()


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    document, preview = await rag.ingest(file.filename or "document", file.content_type, content)
    return UploadResponse(document=document, chunks_preview=preview)


@app.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str) -> DeleteResponse:
    deleted = await rag.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DeleteResponse(deleted=True, document_id=document_id)


@app.post("/query")
async def query_documents(request: QueryRequest):
    return await rag.query(
        question=request.question,
        document_ids=request.document_ids,
        top_k=request.top_k,
        compare=request.mode == "compare"
    )


@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    async def events():
        try:
            response = await rag.query(
                question=request.question,
                document_ids=request.document_ids,
                top_k=request.top_k,
                compare=request.mode == "compare"
            )
            yield _sse(StreamEvent(type="citations", value=response.citations).model_dump(mode="json"))
            for token in response.answer.split(" "):
                yield _sse(StreamEvent(type="token", value=f"{token} ").model_dump(mode="json"))
                await asyncio.sleep(0.018)
            yield _sse(StreamEvent(type="done", value=None).model_dump(mode="json"))
        except Exception as exc:
            yield _sse(StreamEvent(type="error", value=str(exc)).model_dump(mode="json"))

    return StreamingResponse(events(), media_type="text/event-stream")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"
