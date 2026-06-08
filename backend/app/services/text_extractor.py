from __future__ import annotations

import io
import re
from pathlib import Path

from app.services.chunker import PageParagraph


def extract_paragraphs(filename: str, content: bytes) -> tuple[list[PageParagraph], int]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(content)
    if suffix == ".docx":
        return _extract_docx(content)
    return _extract_text(content)


def _extract_pdf(content: bytes) -> tuple[list[PageParagraph], int]:
    try:
        from pypdf import PdfReader
    except Exception:
        return _extract_text(content)

    reader = PdfReader(io.BytesIO(content))
    paragraphs: list[PageParagraph] = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        paragraphs.extend(_paragraphs_for_page(text, page_index))
    return paragraphs, max(1, len(reader.pages))


def _extract_docx(content: bytes) -> tuple[list[PageParagraph], int]:
    try:
        from docx import Document
    except Exception:
        return _extract_text(content)

    doc = Document(io.BytesIO(content))
    paragraphs = [
        PageParagraph(page=1, paragraph=index, text=p.text.strip())
        for index, p in enumerate(doc.paragraphs, start=1)
        if p.text.strip()
    ]
    return paragraphs, 1


def _extract_text(content: bytes) -> tuple[list[PageParagraph], int]:
    text = content.decode("utf-8", errors="ignore")
    return _paragraphs_for_page(text, 1), 1


def _paragraphs_for_page(text: str, page: int) -> list[PageParagraph]:
    raw = [part.strip() for part in re.split(r"\n\s*\n|(?<=\.)\s{2,}", text) if part.strip()]
    if not raw and text.strip():
        raw = [text.strip()]
    return [PageParagraph(page=page, paragraph=index, text=value) for index, value in enumerate(raw, start=1)]
