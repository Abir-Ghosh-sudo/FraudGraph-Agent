"""
Agent-facing evidence tools.

These wrappers expose the existing evidence collection, normalization,
scoring, provenance, and sufficiency components to agent nodes.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from backend.evidence.collector import EvidenceCollector
from backend.evidence.normalizer import EvidenceNormalizer
from backend.evidence.provenance import ProvenanceStore
from backend.evidence.scorer import EvidenceScorer
from backend.evidence.sufficiency import EvidenceSufficiency


class EvidenceTools:
    """Interface for evidence operations available to the agent."""

    def __init__(
        self,
        *,
        collector: EvidenceCollector | None = None,
        normalizer: EvidenceNormalizer | None = None,
        scorer: EvidenceScorer | None = None,
        provenance: ProvenanceStore | None = None,
        sufficiency: EvidenceSufficiency | None = None,
    ) -> None:
        self.collector = collector or EvidenceCollector()
        self.normalizer = normalizer or EvidenceNormalizer()
        self.scorer = scorer or EvidenceScorer()
        self.provenance = provenance or ProvenanceStore()
        self.sufficiency = sufficiency or EvidenceSufficiency()

    def normalize(
        self,
        raw_evidence: Mapping[str, Any],
    ) -> Any:
        """Normalize a raw evidence record."""
        return self.normalizer.normalize(raw_evidence)

    def add(self, evidence: Any) -> Any:
        """Add evidence through the shared collector."""
        return self.collector.add(evidence)

    def add_many(self, evidence: Sequence[Any]) -> list[Any]:
        """Add multiple evidence records."""
        return [self.add(item) for item in evidence]

    def get(self, evidence_id: str) -> Any:
        """Retrieve collected evidence by identifier."""
        for method_name in ("get", "get_by_id"):
            method = getattr(self.collector, method_name, None)
            if method is not None:
                return method(evidence_id)

        raise AttributeError(
            "EvidenceCollector does not expose a supported retrieval method."
        )

    def all(self) -> list[Any]:
        """Return all collected evidence."""
        for method_name in ("all", "list", "values"):
            method = getattr(self.collector, method_name, None)
            if method is not None:
                result = method()
                return list(result)

        raise AttributeError(
            "EvidenceCollector does not expose a supported listing method."
        )

    def score(self, evidence: Any) -> Any:
        """Score the strength of an evidence item."""
        return self.scorer.score(evidence)

    def check_sufficiency(
        self,
        evidence: Sequence[Any],
        *,
        risk_level: Any = None,
    ) -> Any:
        """Determine whether the available evidence is sufficient."""
        return self.sufficiency.evaluate(
            evidence,
            risk_level=risk_level,
        )

    def record_provenance(
        self,
        evidence_id: str,
        provenance: Any,
    ) -> Any:
        """Record provenance for an evidence item."""
        for method_name in ("record", "add", "store"):
            method = getattr(self.provenance, method_name, None)
            if method is not None:
                return method(evidence_id, provenance)

        raise AttributeError(
            "ProvenanceStore does not expose a supported write method."
        )

    def summary(self) -> dict[str, Any]:
        """Return a compact evidence summary for agent reasoning."""
        evidence = self.all()

        return {
            "count": len(evidence),
            "evidence_ids": [
                str(getattr(item, "evidence_id", ""))
                for item in evidence
            ],
        }


def create_evidence_tools(
    *,
    collector: EvidenceCollector | None = None,
    normalizer: EvidenceNormalizer | None = None,
    scorer: EvidenceScorer | None = None,
    provenance: ProvenanceStore | None = None,
    sufficiency: EvidenceSufficiency | None = None,
) -> EvidenceTools:
    """Create the default evidence-tool collection."""
    return EvidenceTools(
        collector=collector,
        normalizer=normalizer,
        scorer=scorer,
        provenance=provenance,
        sufficiency=sufficiency,
    )