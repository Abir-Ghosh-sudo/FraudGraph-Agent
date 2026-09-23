"""
Evidence normalization utilities.

Converts common raw evidence representations into the project's
canonical Evidence schema without inventing missing evidence.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from backend.app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
    EvidenceStrength,
    EvidenceType,
)


class EvidenceNormalizer:
    """Normalize raw evidence into canonical Evidence objects."""

    def normalize(
        self,
        raw: Any,
        *,
        default_source_type: EvidenceSourceType = EvidenceSourceType.EXTERNAL,
        default_evidence_type: EvidenceType = EvidenceType.CONTEXTUAL,
        default_strength: EvidenceStrength = EvidenceStrength.MODERATE,
    ) -> Evidence | None:
        """Normalize one raw evidence item."""
        if raw is None:
            return None

        if isinstance(raw, Evidence):
            return raw

        if not isinstance(raw, Mapping):
            return None

        evidence_id = self._first(
            raw,
            "evidence_id",
            "id",
        )

        if not evidence_id:
            return None

        source_type = self._enum_value(
            EvidenceSourceType,
            self._first(
                raw,
                "source_type",
                "source",
            ),
            default_source_type,
        )

        evidence_type = self._enum_value(
            EvidenceType,
            self._first(
                raw,
                "evidence_type",
                "type",
            ),
            default_evidence_type,
        )

        strength = self._enum_value(
            EvidenceStrength,
            self._first(
                raw,
                "strength",
                "evidence_strength",
            ),
            default_strength,
        )

        return Evidence(
            evidence_id=str(evidence_id),
            source_type=source_type,
            evidence_type=evidence_type,
            strength=strength,
            title=self._optional_string(
                self._first(raw, "title", "name")
            ),
            description=self._optional_string(
                self._first(raw, "description", "summary", "reason")
            ),
            data=dict(
                self._first(
                    raw,
                    "data",
                    "properties",
                    "metadata",
                )
                or {}
            ),
        )

    def normalize_many(
        self,
        raw_items: Iterable[Any],
        **kwargs: Any,
    ) -> list[Evidence]:
        """Normalize multiple raw evidence items."""
        normalized: list[Evidence] = []

        for item in raw_items:
            evidence = self.normalize(item, **kwargs)

            if evidence is not None:
                normalized.append(evidence)

        return normalized

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            value = data.get(key)

            if value is not None:
                return value

        return None

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @staticmethod
    def _enum_value(
        enum_cls: Any,
        value: Any,
        default: Any,
    ) -> Any:
        if value is None:
            return default

        if isinstance(value, enum_cls):
            return value

        normalized = str(value).strip().lower()

        for member in enum_cls:
            if str(member.value).lower() == normalized:
                return member

            if member.name.lower() == normalized:
                return member

        return default