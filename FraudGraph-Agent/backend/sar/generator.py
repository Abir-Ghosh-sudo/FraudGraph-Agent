from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from uuid import uuid4


@dataclass(slots=True)
class SARReport:
    """Structured Suspicious Activity Report representation."""

    report_id: str
    case_id: str | None
    investigation_id: str | None
    subject: dict[str, Any]
    suspicious_activity: dict[str, Any]
    evidence: list[dict[str, Any]]
    rationale: list[str]
    policy_references: list[str]
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: str = "DRAFT"

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "case_id": self.case_id,
            "investigation_id": self.investigation_id,
            "subject": dict(self.subject),
            "suspicious_activity": dict(self.suspicious_activity),
            "evidence": list(self.evidence),
            "rationale": list(self.rationale),
            "policy_references": list(self.policy_references),
            "generated_at": self.generated_at.isoformat(),
            "status": self.status,
        }


class SARGenerator:
    """
    Generates a structured SAR draft from investigation results.

    This layer prepares investigation facts for review. It does not submit
    the report to a regulator and does not claim regulatory filing has
    occurred.
    """

    def __init__(
        self,
        *,
        default_status: str = "DRAFT",
    ) -> None:
        self.default_status = default_status

    def generate(
        self,
        *,
        case_id: str | None = None,
        investigation_id: str | None = None,
        subject: Mapping[str, Any] | None = None,
        risk_score: float | None = None,
        risk_level: str | None = None,
        fraud_type: str | None = None,
        confidence: float | None = None,
        findings: Iterable[Any] | None = None,
        evidence: Iterable[Any] | None = None,
        actions: Iterable[Any] | None = None,
        rationale: Iterable[str] | None = None,
        policy_references: Iterable[str] | None = None,
        policy_result: Any | None = None,
    ) -> SARReport:
        """
        Build a SAR draft from normalized investigation information.
        """

        normalized_findings = [
            self._normalize_item(item)
            for item in (findings or [])
        ]

        normalized_evidence = [
            self._normalize_item(item)
            for item in (evidence or [])
        ]

        normalized_actions = [
            self._normalize_item(item)
            for item in (actions or [])
        ]

        reasons = [
            str(item)
            for item in (rationale or [])
            if str(item).strip()
        ]

        references = [
            str(item)
            for item in (policy_references or [])
            if str(item).strip()
        ]

        if policy_result is not None:
            policy_data = self._normalize_item(policy_result)

            reasons.extend(
                str(reason)
                for reason in policy_data.get("reasons", [])
                if str(reason).strip()
            )

            references.extend(
                str(reference)
                for reference in policy_data.get(
                    "policy_references",
                    [],
                )
                if str(reference).strip()
            )

        normalized_reasons = self._deduplicate(reasons)
        normalized_references = self._deduplicate(references)

        normalized_score = self._normalize_score(risk_score)
        normalized_confidence = self._normalize_score(confidence)

        suspicious_activity = {
            "risk_score": normalized_score,
            "risk_level": risk_level,
            "fraud_type": fraud_type,
            "confidence": normalized_confidence,
            "findings": normalized_findings,
            "actions": normalized_actions,
        }

        return SARReport(
            report_id=f"sar-{uuid4().hex}",
            case_id=case_id,
            investigation_id=investigation_id,
            subject=dict(subject or {}),
            suspicious_activity=suspicious_activity,
            evidence=normalized_evidence,
            rationale=normalized_reasons,
            policy_references=normalized_references,
            status=self.default_status,
        )

    def generate_from_investigation(
        self,
        investigation: Mapping[str, Any] | Any,
        *,
        evidence: Iterable[Any] | None = None,
        findings: Iterable[Any] | None = None,
        policy_result: Any | None = None,
    ) -> SARReport:
        """Generate a SAR draft directly from an investigation object."""

        data = self._normalize_item(investigation)

        assessment = data.get("assessment", {})
        if not isinstance(assessment, Mapping):
            assessment = {}

        result = data.get("result", {})
        if not isinstance(result, Mapping):
            result = {}

        investigation_findings = (
            findings
            if findings is not None
            else result.get("findings", [])
        )

        investigation_evidence = (
            evidence
            if evidence is not None
            else result.get("evidence", [])
        )

        rationale = []

        if assessment.get("rationale"):
            rationale.append(
                str(assessment["rationale"])
            )

        recommendations = result.get(
            "recommendations",
            [],
        )

        if isinstance(recommendations, Iterable) and not isinstance(
            recommendations,
            (str, bytes, Mapping),
        ):
            for recommendation in recommendations:
                if isinstance(recommendation, Mapping):
                    text = (
                        recommendation.get("rationale")
                        or recommendation.get("reason")
                        or recommendation.get("description")
                    )
                    if text:
                        rationale.append(str(text))

        return self.generate(
            case_id=data.get("case_id"),
            investigation_id=data.get("investigation_id"),
            subject=data.get(
                "subject",
                data.get("customer", {}),
            ),
            risk_score=assessment.get("risk_score"),
            risk_level=assessment.get("risk_level"),
            fraud_type=assessment.get("fraud_type"),
            confidence=assessment.get("confidence"),
            findings=investigation_findings,
            evidence=investigation_evidence,
            actions=data.get("actions", []),
            rationale=rationale,
            policy_result=policy_result,
        )

    @staticmethod
    def _normalize_item(item: Any) -> dict[str, Any]:
        if item is None:
            return {}

        if isinstance(item, Mapping):
            return dict(item)

        if hasattr(item, "model_dump"):
            try:
                value = item.model_dump()
                if isinstance(value, Mapping):
                    return dict(value)
            except Exception:
                pass

        if hasattr(item, "to_dict"):
            try:
                value = item.to_dict()
                if isinstance(value, Mapping):
                    return dict(value)
            except Exception:
                pass

        if hasattr(item, "__dataclass_fields__"):
            try:
                from dataclasses import asdict

                value = asdict(item)
                if isinstance(value, Mapping):
                    return dict(value)
            except Exception:
                pass

        if hasattr(item, "__dict__"):
            return {
                str(key): value
                for key, value in vars(item).items()
                if not str(key).startswith("_")
            }

        return {"value": item}

    @staticmethod
    def _normalize_score(value: Any) -> float | None:
        if value is None:
            return None

        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _deduplicate(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)

        return result