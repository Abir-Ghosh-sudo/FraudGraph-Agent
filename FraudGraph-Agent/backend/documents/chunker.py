from __future__ import annotations

from typing import Any


class DocumentChunker:
    """Chunks text into segments with configurable character size and overlap."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        self.chunk_size = max(100, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size - 1))

    def chunk_text(self, text: str, extra_meta: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not text.strip():
            return []

        chunks: list[dict[str, Any]] = []
        meta = extra_meta or {}
        start = 0
        text_len = len(text)
        step = self.chunk_size - self.chunk_overlap
        idx = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(
                    {
                        "chunk_index": idx,
                        "text": chunk_content,
                        "char_start": start,
                        "char_end": end,
                        **meta,
                    }
                )
                idx += 1
            if end >= text_len:
                break
            start += step

        return chunks
