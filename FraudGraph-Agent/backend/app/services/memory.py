from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.errors import MemoryNotFoundError
from backend.app.logging import get_logger

logger = get_logger(__name__)


class MemoryEntry:
    def __init__(
        self,
        memory_id: str,
        case_id: str,
        investigation_id: str,
        outcome: str | None,
        findings: list[str],
        decisions: list[str],
        actions: list[str],
        metadata: dict[str, Any],
        created_at: datetime,
    ) -> None:
        self.memory_id = memory_id
        self.case_id = case_id
        self.investigation_id = investigation_id
        self.outcome = outcome
        self.findings = findings
        self.decisions = decisions
        self.actions = actions
        self.metadata = metadata
        self.created_at = created_at
        self._text = self._build_text()

    def _build_text(self) -> str:
        parts = []
        if self.outcome:
            parts.append(f"outcome:{self.outcome}")
        parts.extend(self.findings[:5])
        parts.extend(self.decisions[:5])
        parts.extend(self.actions[:3])
        fraud_type = self.metadata.get("fraud_type", "")
        if fraud_type:
            parts.append(f"fraud_type:{fraud_type}")
        return " ".join(parts).lower()

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "case_id": self.case_id,
            "investigation_id": self.investigation_id,
            "outcome": self.outcome,
            "findings": self.findings,
            "decisions": self.decisions,
            "actions": self.actions,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class MemoryService:
    """
    Case memory service.

    Stores investigation outcomes and retrieves historically similar cases.
    Uses FAISS vector similarity when embeddings are configured;
    falls back to keyword overlap otherwise.

    Does NOT fabricate historical cases — returns empty results when no
    memories have been stored.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._entries: dict[str, MemoryEntry] = {}
        self._embeddings_model: Any = None
        self._index: Any = None
        self._index_ids: list[str] = []
        self._embeddings_initialized = False

    def store(
        self,
        *,
        case_id: str,
        investigation_id: str,
        outcome: str | None = None,
        findings: list[str] | None = None,
        decisions: list[str] | None = None,
        actions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if not self.settings.case_memory_enabled:
            logger.debug("case memory disabled; not storing")
            return ""

        memory_id = f"mem_{uuid4().hex[:12]}"
        entry = MemoryEntry(
            memory_id=memory_id,
            case_id=case_id,
            investigation_id=investigation_id,
            outcome=outcome,
            findings=findings or [],
            decisions=decisions or [],
            actions=actions or [],
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )

        self._entries[memory_id] = entry

        # Invalidate vector index so it rebuilds on next search
        self._index = None
        self._index_ids = []
        self._embeddings_initialized = False

        logger.info(
            "memory stored",
            memory_id=memory_id,
            case_id=case_id,
            outcome=outcome,
        )

        return memory_id

    def get(self, memory_id: str) -> MemoryEntry:
        entry = self._entries.get(memory_id)
        if entry is None:
            raise MemoryNotFoundError(f"Memory '{memory_id}' not found.")
        return entry

    def search(
        self,
        query_context: dict[str, Any],
        *,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve historically similar cases.

        Returns empty list when no memories have been stored — never fabricates.
        """
        if not self.settings.case_memory_enabled:
            return []

        if not self._entries:
            return []

        k = min(
            top_k or self.settings.case_memory_top_k,
            len(self._entries),
        )

        query_text = self._build_query_text(query_context)

        if self.settings.embeddings_configured:
            results = self._vector_search(query_text, k)
        else:
            results = self._keyword_search(query_text, k)

        return results

    def _build_query_text(self, context: dict[str, Any]) -> str:
        parts = []
        for key in ("fraud_type", "outcome", "risk_level", "patterns"):
            value = context.get(key)
            if isinstance(value, list):
                parts.extend(str(v) for v in value)
            elif value:
                parts.append(str(value))
        findings = context.get("findings", [])
        if isinstance(findings, list):
            parts.extend(str(f) for f in findings[:3])
        return " ".join(parts).lower()

    def _vector_search(self, query_text: str, k: int) -> list[dict[str, Any]]:
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer

            if not self._embeddings_initialized:
                model = SentenceTransformer(self.settings.embedding_model)
                self._embeddings_model = model

                all_ids = list(self._entries.keys())
                texts = [self._entries[mid]._text for mid in all_ids]
                embeddings = model.encode(texts, show_progress_bar=False)
                embeddings = np.array(embeddings, dtype=np.float32)
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1.0, norms)
                embeddings /= norms

                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim)
                index.add(embeddings)  # type: ignore[arg-type]

                self._index = index
                self._index_ids = all_ids
                self._embeddings_initialized = True

            query_emb = self._embeddings_model.encode([query_text])
            query_emb = np.array(query_emb, dtype=np.float32)
            norm = np.linalg.norm(query_emb)
            if norm > 0:
                query_emb /= norm

            scores, indices = self._index.search(query_emb, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._index_ids):
                    continue
                mid = self._index_ids[idx]
                entry = self._entries.get(mid)
                if entry is None:
                    continue
                data = entry.to_dict()
                data["similarity"] = float(score)
                results.append(data)
            return results

        except (ImportError, Exception) as exc:
            logger.warning("vector search failed; falling back to keyword", error=str(exc))
            return self._keyword_search(query_text, k)

    def _keyword_search(self, query_text: str, k: int) -> list[dict[str, Any]]:
        query_terms = set(query_text.split())
        if not query_terms:
            return []

        scored: list[tuple[float, MemoryEntry]] = []
        for entry in self._entries.values():
            entry_terms = set(entry._text.split())
            overlap = len(query_terms & entry_terms)
            if overlap == 0:
                continue
            score = overlap / max(len(query_terms), 1)
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, entry in scored[:k]:
            data = entry.to_dict()
            data["similarity"] = score
            results.append(data)
        return results
