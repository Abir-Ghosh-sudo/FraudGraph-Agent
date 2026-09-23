from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentChunk:
    chunk_id: str
    source_file: str
    source_type: str  # "pdf" | "txt"
    page: int
    offset: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentLoader:
    """
    Discovers and loads policy/regulatory documents from the documents directory.

    Supports PDF (.pdf) and plain text (.txt) files.
    Reports clearly if no documents are found — this is not an error state.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._chunks: list[DocumentChunk] = []
        self._loaded = False

    def discover_files(self) -> list[Path]:
        """Return list of supported document files from documents_dir."""
        documents_dir = self.settings.documents_dir

        if not documents_dir.exists():
            logger.info(
                "documents_dir does not exist",
                path=str(documents_dir),
            )
            return []

        found = sorted(
            p
            for p in documents_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS
        )

        logger.info(
            "discovered document files",
            count=len(found),
            directory=str(documents_dir),
        )

        return found

    def load_all(self) -> list[DocumentChunk]:
        """Load and chunk all discovered documents."""
        if self._loaded:
            return self._chunks

        files = self.discover_files()

        if not files:
            logger.info("no policy/regulatory documents found; GraphRAG will have no document context")
            self._loaded = True
            return []

        all_chunks: list[DocumentChunk] = []

        for file_path in files:
            try:
                chunks = self._load_file(file_path)
                all_chunks.extend(chunks)
                logger.info(
                    "loaded document",
                    file=file_path.name,
                    chunks=len(chunks),
                )
            except Exception as exc:
                logger.warning(
                    "failed to load document; skipping",
                    file=str(file_path),
                    error=str(exc),
                )

        self._chunks = all_chunks
        self._loaded = True

        logger.info("document loading complete", total_chunks=len(all_chunks))

        return self._chunks

    def _load_file(self, file_path: Path) -> list[DocumentChunk]:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._load_pdf(file_path)

        return self._load_text(file_path)

    def _load_text(self, file_path: Path) -> list[DocumentChunk]:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return self._chunk_text(
            text=text,
            source_file=str(file_path),
            source_type="txt",
        )

    def _load_pdf(self, file_path: Path) -> list[DocumentChunk]:
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.warning(
                "pypdf not installed; skipping PDF",
                file=str(file_path),
            )
            return []

        reader = PdfReader(str(file_path))
        chunks: list[DocumentChunk] = []

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_chunks = self._chunk_text(
                text=page_text,
                source_file=str(file_path),
                source_type="pdf",
                base_page=page_num,
            )
            chunks.extend(page_chunks)

        return chunks

    def _chunk_text(
        self,
        text: str,
        source_file: str,
        source_type: str,
        base_page: int = 0,
    ) -> list[DocumentChunk]:
        chunk_size = self.settings.document_chunk_size
        overlap = self.settings.document_chunk_overlap

        if not text.strip():
            return []

        chunks: list[DocumentChunk] = []
        offset = 0

        while offset < len(text):
            end = min(offset + chunk_size, len(text))
            chunk_text = text[offset:end].strip()

            if chunk_text:
                chunk_id = _make_chunk_id(source_file, offset)
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        source_file=source_file,
                        source_type=source_type,
                        page=base_page,
                        offset=offset,
                        text=chunk_text,
                        metadata={
                            "source_file": source_file,
                            "page": base_page,
                            "offset": offset,
                            "chunk_size": len(chunk_text),
                        },
                    )
                )

            if end >= len(text):
                break

            offset = end - overlap

        return chunks


def _make_chunk_id(source_file: str, offset: int) -> str:
    raw = f"{source_file}:{offset}"
    return "chunk_" + hashlib.sha1(raw.encode()).hexdigest()[:12]
