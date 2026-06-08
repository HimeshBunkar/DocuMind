from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.models.schemas import DocumentMeta


class DocumentStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._documents: dict[str, DocumentMeta] = {}
        self.collection = self._create_collection()
        Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)

    def create(self, filename: str, file_type: str) -> DocumentMeta:
        document = DocumentMeta(
            id=str(uuid4()),
            name=filename,
            file_type=file_type,
            status="processing",
            uploaded_at=datetime.now(UTC)
        )
        self._documents[document.id] = document
        self._upsert_mongo(document)
        return document

    def update(self, document: DocumentMeta) -> DocumentMeta:
        self._documents[document.id] = document
        self._upsert_mongo(document)
        return document

    def list(self) -> list[DocumentMeta]:
        if self.collection is not None:
            records = self.collection.find({}, {"_id": 0}).sort("uploaded_at", -1)
            return [DocumentMeta.model_validate(record) for record in records]
        return sorted(self._documents.values(), key=lambda doc: doc.uploaded_at, reverse=True)

    def get(self, document_id: str) -> DocumentMeta | None:
        if self.collection is not None:
            record = self.collection.find_one({"id": document_id}, {"_id": 0})
            return DocumentMeta.model_validate(record) if record else None
        return self._documents.get(document_id)

    def delete(self, document_id: str) -> bool:
        deleted = self._documents.pop(document_id, None) is not None
        if self.collection is not None:
            result = self.collection.delete_one({"id": document_id})
            deleted = deleted or result.deleted_count > 0
        return deleted

    def _create_collection(self):
        if not self.settings.mongodb_uri:
            return None
        try:
            from pymongo import MongoClient

            client = MongoClient(self.settings.mongodb_uri, serverSelectionTimeoutMS=1500)
            client.admin.command("ping")
            return client.get_database("documind").get_collection("documents")
        except Exception:
            return None

    def _upsert_mongo(self, document: DocumentMeta) -> None:
        if self.collection is None:
            return
        payload = document.model_dump(mode="json")
        self.collection.update_one({"id": document.id}, {"$set": payload}, upsert=True)
