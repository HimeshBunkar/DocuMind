from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PageParagraph:
    page: int
    paragraph: int
    text: str


class RecursiveChunker:
    def __init__(self, chunk_size: int = 950, chunk_overlap: int = 160) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split(self, paragraphs: list[PageParagraph]) -> list[PageParagraph]:
        chunks: list[PageParagraph] = []
        for item in paragraphs:
            clean_text = re.sub(r"\s+", " ", item.text).strip()
            if not clean_text:
                continue
            pieces = self._split_text(clean_text, 0)
            for piece in pieces:
                chunks.append(PageParagraph(page=item.page, paragraph=item.paragraph, text=piece))
        return chunks

    def _split_text(self, text: str, separator_index: int) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        separator = self.separators[min(separator_index, len(self.separators) - 1)]
        if separator:
            parts = text.split(separator)
        else:
            parts = list(text)

        if len(parts) == 1:
            return self._split_text(text, separator_index + 1)

        chunks: list[str] = []
        current = ""
        for part in parts:
            candidate = part if not current else f"{current}{separator}{part}"
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.extend(self._with_overlap(current))
            current = part
        if current:
            chunks.extend(self._with_overlap(current))

        normalized: list[str] = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                normalized.append(chunk.strip())
            else:
                normalized.extend(self._split_text(chunk, separator_index + 1))
        return [chunk for chunk in normalized if chunk]

    def _with_overlap(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end].strip())
            if end == len(text):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks
