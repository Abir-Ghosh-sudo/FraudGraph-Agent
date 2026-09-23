from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(slots=True)
class SARPolicyResult:
    """Result of evaluating whether an investigation requires a SAR."""

    required: bool
    reasons: list[str] = field(default_factory=list)
    risk_level: str | None = None
    fraud_type: str | None = None
    confidence: float | None = None
    approval_required: bool = True
    policy_references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": self.required,
            "reasons": list(self.reasons),
            "risk_level": self.risk_level,
            "fraud_type": self.fraud_type,
            "confidence": self.confidence,
            "approval_required": self.approval_required,
            "policy_references": list(self.policy_references),
        }


class SARPolicyChecker:
    """
    Deterministic SAR policy evaluation layer.

    The checker does not invent regulatory requirements. It evaluates the
    policy configuration supplied by the application and records the
    evidence/reasons behind the result.

    A custom policy function can be supplied when the HHGOA policy rules
    are loaded from a dataset or external policy source.
    """

    def __init__(
        self,
        *,
        risk_threshold: float = 0.85,
        confidence_threshold: float = 0.70,
        required_risk_levels: Iterable[str] | None = None,
        required_fraud_types: Iterable[str] | None = None,
        custom_policy_fn: Any | None = None,
    ) -> None:
        if not 0.0 <= risk_threshold <= 1.0:
            raise ValueError(
                "risk_threshold must be between 0 and 1"
            )

        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold must be between 0 and 1"
            )

        self.risk_threshold = risk_threshold
        self.confidence_threshold = confidence_threshold

        self.required_risk_levels = {
            str(value).lower()
            for value in (required_risk_levels or {"critical"})
        }

        self.required_fraud_types = {
            str(value).lower()
            for value in (required_fraud_types or set())
        }

        self._custom_policy_fn = custom_policy_fn

    def check(
        self,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        fraud_type: str | None = None,
        confidence: float | None = None,
        findings: Iterable[Any] | None = None,
        evidence: Iterable[Any] | None = None,
        policy_context: Mapping[str, Any] | None = None,
    ) -> SARPolicyResult:
        """
        Evaluate SAR requirements for an investigation.

        Multiple independent policy signals can contribute to the decision.
        The result keeps the reasons separate so the final case explanation
        can show why a SAR was or was not required.
        """

        normalized_score = self._normalize_optional(risk_score)
        normalized_confidence = self._normalize_optional(confidence)

        normalized_level = (
            str(risk_level).lower()
            if risk_level is not None
            else None
        )

        normalized_fraud_type = (
            str(fraud_type).lower()
            if fraud_type is not None
            else None
        )

        if self._custom_policy_fn is not None:
            custom_result = self._run_custom_policy(
                risk_score=normalized_score,
                risk_level=normalized_level,
                fraud_type=normalized_fraud_type,
                confidence=normalized_confidence,
                findings=list(findings or []),
                evidence=list(evidence or []),
                policy_context=policy_context,
            )

            if custom_result is not None:
                return custom_result

        reasons: list[str] = []
        references: list[str] = []

        if (
            normalized_score is not None
            and normalized_score >= self.risk_threshold
        ):
            reasons.append(
                "Risk score meets or exceeds the configured SAR threshold."
            )
            references.append("risk_score_threshold")

        if (
            normalized_level is not None
            and normalized_level in self.required_risk_levels
        ):
            reasons.append(
                f"Risk level '{normalized_level}' is configured "
                "to require SAR review."
            )
            references.append("risk_level_policy")

        if (
            normalized_fraud_type is not None
            and normalized_fraud_type in self.required_fraud_types
        ):
            reasons.append(
                f"Fraud type '{normalized_fraud_type}' is configured "
                "to require SAR review."
            )
            references.append("fraud_type_policy")

        finding_reasons = self._finding_reasons(
            findings or [],
        )
        reasons.extend(finding_reasons)

        evidence_reasons = self._evidence_reasons(
            evidence or [],
        )
        reasons.extend(evidence_reasons)

        if finding_reasons:
            references.append("investigation_findings")

        if evidence_reasons:
            references.append("supporting_evidence")

        if policy_context:
            context_reasons, context_references = (
                self._context_rules(policy_context)
            )
            reasons.extend(context_reasons)
            references.extend(context_references)

        required = bool(reasons)

        return SARPolicyResult(
            required=required,
            reasons=self._deduplicate(reasons),
            risk_level=risk_level,
            fraud_type=fraud_type,
            confidence=normalized_confidence,
            approval_required=True,
            policy_references=self._deduplicate(references),
        )

    def requires_sar(
        self,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        fraud_type: str | None = None,
        confidence: float | None = None,
        policy_context: Mapping[str, Any] | None = None,
    ) -> bool:
        """Convenience method returning only the SAR requirement."""

        result = self.check(
            risk_score=risk_score,
            risk_level=risk_level,
            fraud_type=fraud_type,
            confidence=confidence,
            policy_context=policy_context,
        )

        return result.required

    def _run_custom_policy(
        self,
        **kwargs: Any,
    ) -> SARPolicyResult | None:
        try:
            result = self._custom_policy_fn(**kwargs)
        except TypeError:
            try:
                result = self._custom_policy_fn(
                    kwargs["risk_score"],
                    kwargs["risk_level"],
                    kwargs["fraud_type"],
                    kwargs["confidence"],
                )
            except Exception:
                return None
        except Exception:
            return None

        if isinstance(result, SARPolicyResult):
            return result

        if isinstance(result, Mapping):
            return SARPolicyResult(
                required=bool(result.get("required", False)),
                reasons=[
                    str(reason)
                    for reason in result.get("reasons", [])
                ],
                risk_level=result.get(
                    "risk_level",
                    kwargs.get("risk_level"),
                ),
                fraud_type=result.get(
                    "fraud_type",
                    kwargs.get("fraud_type"),
                ),
                confidence=self._normalize_optional(
                    result.get(
                        "confidence",
                        kwargs.get("confidence"),
                    )
                ),
                approval_required=bool(
                    result.get("approval_required", True)
                ),
                policy_references=[
                    str(reference)
                    for reference in result.get(
                        "policy_references",
                        [],
                    )
                ],
            )

        return None

    @staticmethod
    def _finding_reasons(
        findings: Iterable[Any],
    ) -> list[str]:
        reasons: list[str] = []

        for finding in findings:
            if isinstance(finding, Mapping):
                finding_type = (
                    finding.get("fraud_type")
                    or finding.get("pattern")
                    or finding.get("type")
                )
                confidence = finding.get("confidence")

                if finding_type:
                    if confidence is not None:
                        try:
                            confidence_text = (
                                f" (confidence={float(confidence):.2f})"
                            )
                        except (TypeError, ValueError):
                            confidence_text = ""
                    else:
                        confidence_text = ""

                    reasons.append(
                        f"Investigation finding indicates "
                        f"potential fraud pattern '{finding_type}'"
                        f"{confidence_text}."
                    )

            else:
                finding_type = getattr(
                    finding,
                    "fraud_type",
                    None,
                ) or getattr(
                    finding,
                    "pattern",
                    None,
                )

                if finding_type:
                    reasons.append(
                        f"Investigation finding indicates "
                        f"potential fraud pattern '{finding_type}'."
                    )

        return reasons

    @staticmethod
    def _evidence_reasons(
        evidence: Iterable[Any],
    ) -> list[str]:
        reasons: list[str] = []

        for item in evidence:
            if isinstance(item, Mapping):
                evidence_type = (
                    item.get("evidence_type")
                    or item.get("type")
                )
                description = (
                    item.get("description")
                    or item.get("title")
                )
            else:
                evidence_type = getattr(
                    item,
                    "evidence_type",
                    None,
                ) or getattr(item, "type", None)

                description = getattr(
                    item,
                    "description",
                    None,
                ) or getattr(item, "title", None)

            if evidence_type:
                label = str(description or evidence_type)
                reasons.append(
                    f"Supporting investigation evidence: {label}."
                )

        return reasons

    @staticmethod
    def _context_rules(
        context: Mapping[str, Any],
    ) -> tuple[list[str], list[str]]:
        reasons: list[str] = []
        references: list[str] = []

        if context.get("sar_required") is True:
            reasons.append(
                "The supplied policy context explicitly requires "
                "SAR review."
            )
            references.append("explicit_sar_requirement")

        if context.get("regulatory_report_required") is True:
            reasons.append(
                "The supplied policy context marks the investigation "
                "for regulatory reporting."
            )
            references.append("regulatory_reporting_requirement")

        if context.get("manual_sar_review") is True:
            reasons.append(
                "The supplied policy context requests manual SAR review."
            )
            references.append("manual_sar_review")

        return reasons, references

    @staticmethod
    def _normalize_optional(value: Any) -> float | None:
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