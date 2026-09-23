from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .outcomes import CaseOutcome, OutcomeStore


@dataclass(frozen=True)
class MemoryMatch:
    """A previous case/outcome relevant to the current investigation."""

    case_id: str
    score: float
    outcome: CaseOutcome
    matched_features: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "score": self.score,
            "matched_features": list(self.matched_features),
            "outcome": self.outcome.to_dict(),
        }


class MemoryRetriever:
    """Retrieve prior investigation outcomes using lightweight feature matching."""

    def __init__(
        self,
        outcome_store: OutcomeStore | None = None,
    ) -> None:
        self.outcome_store = outcome_store or OutcomeStore()

    def retrieve(
        self,
        *,
        case_id: str | None = None,
        outcome: str | None = None,
        action: str | None = None,
        risk_level: str | None = None,
        fraud_confirmed: bool | None = None,
        findings: Iterable[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryMatch]:
        if limit <= 0:
            return []

        query_findings = {
            str(item).strip().lower()
            for item in (findings or ())
            if str(item).strip()
        }

        candidates: list[CaseOutcome] = []

        if outcome is not None:
            candidates.extend(
                self.outcome_store.find_by_outcome(outcome)
            )
        elif action is not None:
            candidates.extend(
                self.outcome_store.find_by_action(action)
            )
        else:
            for stored_case in self._case_ids():
                candidates.extend(
                    self.outcome_store.list_for_case(stored_case)
                )

        matches: list[MemoryMatch] = []

        for candidate in candidates:
            if case_id is not None and candidate.case_id == case_id:
                continue

            score, features = self._score(
                candidate=candidate,
                outcome=outcome,
                action=action,
                risk_level=risk_level,
                fraud_confirmed=fraud_confirmed,
                findings=query_findings,
            )

            if score <= 0:
                continue

            matches.append(
                MemoryMatch(
                    case_id=candidate.case_id,
                    score=score,
                    outcome=candidate,
                    matched_features=tuple(features),
                )
            )

        matches.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return matches[:limit]

    def similar_cases(
        self,
        *,
        risk_level: str | None = None,
        fraud_confirmed: bool | None = None,
        findings: Iterable[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryMatch]:
        return self.retrieve(
            risk_level=risk_level,
            fraud_confirmed=fraud_confirmed,
            findings=findings,
            limit=limit,
        )

    def _score(
        self,
        *,
        candidate: CaseOutcome,
        outcome: str | None,
        action: str | None,
        risk_level: str | None,
        fraud_confirmed: bool | None,
        findings: set[str],
    ) -> tuple[float, list[str]]:
        score = 0.0
        features: list[str] = []

        if outcome is not None and candidate.outcome == outcome:
            score += 0.35
            features.append("outcome")

        if action is not None and candidate.action == action:
            score += 0.25
            features.append("action")

        if (
            risk_level is not None
            and candidate.risk_level == risk_level
        ):
            score += 0.15
            features.append("risk_level")

        if (
            fraud_confirmed is not None
            and candidate.fraud_confirmed == fraud_confirmed
        ):
            score += 0.15
            features.append("fraud_confirmed")

        candidate_findings = {
            item.strip().lower()
            for item in candidate.findings
            if item.strip()
        }

        if findings and candidate_findings:
            overlap = findings & candidate_findings

            if overlap:
                ratio = len(overlap) / len(findings)
                score += min(0.10, ratio * 0.10)
                features.append("findings")

        return min(score, 1.0), features

    def _case_ids(self) -> list[str]:
        case_ids: set[str] = set()

        for outcome in self._all_outcomes():
            case_ids.add(outcome.case_id)

        return list(case_ids)

    def _all_outcomes(self) -> list[CaseOutcome]:
        outcomes: list[CaseOutcome] = []

        for case_id in self._known_case_ids():
            outcomes.extend(
                self.outcome_store.list_for_case(case_id)
            )

        return outcomes

    def _known_case_ids(self) -> set[str]:
        case_ids: set[str] = set()

        for outcome in self.outcome_store.find_confirmed_fraud():
            case_ids.add(outcome.case_id)

        for outcome in self.outcome_store.find_by_outcome(
            "cleared"
        ):
            case_ids.add(outcome.case_id)

        for outcome in self.outcome_store.find_by_action(
            "monitor"
        ):
            case_ids.add(outcome.case_id)

        for outcome in self.outcome_store.find_by_action(
            "block"
        ):
            case_ids.add(outcome.case_id)

        return case_ids