from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.logging import get_logger

logger = get_logger("documents.parser")


class DocumentParser:
    """Parses text and PDF files into structured page content."""

    def parse_file(self, path: Path) -> list[dict[str, Any]]:
        """Returns list of {'page': int, 'text': str}."""
        if not path.exists():
            return []

        suffix = path.suffix.lower()
        if suffix in (".txt", ".md", ".csv", ".json"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                return [{"page": 1, "text": text}]
            except Exception as exc:
                logger.error("failed_parsing_text_file", path=str(path), error=str(exc))
                return []
        elif suffix == ".pdf":
            return self._parse_pdf(path)

        return []

    def _parse_pdf(self, path: Path) -> list[dict[str, Any]]:
        pages: list[dict[str, Any]] = []
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({"page": i + 1, "text": text})
        except ImportError:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(path))
                for i, page in enumerate(doc):
                    pages.append({"page": i + 1, "text": page.get_text()})
            except ImportError:
                logger.warning("no_pdf_parser_installed_install_pypdf", path=str(path))
        except Exception as exc:
            logger.error("pdf_parse_error", path=str(path), error=str(exc))
        return pages
