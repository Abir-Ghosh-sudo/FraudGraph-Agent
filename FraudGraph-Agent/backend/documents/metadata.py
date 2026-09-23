from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class DocumentMetadata:
    doc_id: str
    file_path: str
    file_type: str
    title: str = ""
    num_pages: int = 1
    num_chunks: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    extra: dict[str, Any] = field(default_factory=dict)
