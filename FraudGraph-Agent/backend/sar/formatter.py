from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Mapping

from backend.sar.generator import SARReport


class SARFormatter:
    """Formats SAR drafts for API, storage, or human review."""

    def to_dict(
        self,
        report: SARReport | Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a JSON-compatible dictionary."""

        data = self._normalize(report)
        return self._make_json_safe(data)

    def to_json(
        self,
        report: SARReport | Mapping[str, Any],
        *,
        indent: int = 2,
    ) -> str:
        """Serialize a SAR report to JSON."""

        return json.dumps(
            self.to_dict(report),
            indent=indent,
            ensure_ascii=False,
            sort_keys=False,
        )

    def to_text(
        self,
        report: SARReport | Mapping[str, Any],
    ) -> str:
        """Create a concise human-readable SAR review document."""

        data = self.to_dict(report)

        lines = [
            "SUSPICIOUS ACTIVITY REPORT — DRAFT",
            "",
            f"Report ID: {data.get('report_id', '')}",
            f"Case ID: {data.get('case_id') or 'N/A'}",
            (
                "Investigation ID: "
                f"{data.get('investigation_id') or 'N/A'}"
            ),
            f"Status: {data.get('status', 'DRAFT')}",
            f"Generated At: {data.get('generated_at', '')}",
            "",
            "SUBJECT",
            "-------",
        ]

        subject = data.get("subject", {})
        if isinstance(subject, Mapping) and subject:
            for key, value in subject.items():
                lines.append(
                    f"{self._display_name(key)}: {value}"
                )
        else:
            lines.append("No subject information supplied.")

        activity = data.get("suspicious_activity", {})
        if not isinstance(activity, Mapping):
            activity = {}

        lines.extend(
            [
                "",
                "SUSPICIOUS ACTIVITY",
                "-------------------",
                (
                    "Risk Score: "
                    f"{self._display_value(activity.get('risk_score'))}"
                ),
                (
                    "Risk Level: "
                    f"{self._display_value(activity.get('risk_level'))}"
                ),
                (
                    "Fraud Type: "
                    f"{self._display_value(activity.get('fraud_type'))}"
                ),
                (
                    "Confidence: "
                    f"{self._display_value(activity.get('confidence'))}"
                ),
            ]
        )

        self._append_items(
            lines,
            "FINDINGS",
            activity.get("findings", []),
        )

        self._append_items(
            lines,
            "ACTIONS",
            activity.get("actions", []),
        )

        self._append_items(
            lines,
            "SUPPORTING EVIDENCE",
            data.get("evidence", []),
        )

        self._append_strings(
            lines,
            "RATIONALE",
            data.get("rationale", []),
        )

        self._append_strings(
            lines,
            "POLICY REFERENCES",
            data.get("policy_references", []),
        )

        lines.extend(
            [
                "",
                "This document is a draft generated from "
                "investigation data and requires appropriate review "
                "before any regulatory submission.",
            ]
        )

        return "\n".join(lines)

    def to_submission_payload(
        self,
        report: SARReport | Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Produce a clean payload suitable for a downstream filing adapter.

        No external filing is performed by this formatter.
        """

        data = self.to_dict(report)

        return {
            "report_id": data.get("report_id"),
            "case_id": data.get("case_id"),
            "investigation_id": data.get("investigation_id"),
            "subject": data.get("subject", {}),
            "suspicious_activity": data.get(
                "suspicious_activity",
                {},
            ),
            "evidence": data.get("evidence", []),
            "rationale": data.get("rationale", []),
            "policy_references": data.get(
                "policy_references",
                [],
            ),
            "generated_at": data.get("generated_at"),
            "status": data.get("status", "DRAFT"),
        }

    @staticmethod
    def _normalize(
        report: SARReport | Mapping[str, Any],
    ) -> dict[str, Any]:
        if isinstance(report, SARReport):
            return report.to_dict()

        if isinstance(report, Mapping):
            return dict(report)

        if hasattr(report, "to_dict"):
            value = report.to_dict()
            if isinstance(value, Mapping):
                return dict(value)

        if hasattr(report, "model_dump"):
            value = report.model_dump()
            if isinstance(value, Mapping):
                return dict(value)

        raise TypeError(
            "report must be SARReport or a mapping"
        )

    @classmethod
    def _make_json_safe(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Mapping):
            return {
                str(key): cls._make_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set, frozenset)):
            return [
                cls._make_json_safe(item)
                for item in value
            ]

        if hasattr(value, "value"):
            try:
                return cls._make_json_safe(value.value)
            except Exception:
                pass

        return value

    @staticmethod
    def _display_name(value: Any) -> str:
        text = str(value).replace("_", " ").strip()
        return text.title()

    @staticmethod
    def _display_value(value: Any) -> str:
        if value is None:
            return "N/A"

        if isinstance(value, float):
            return f"{value:.4f}"

        return str(value)

    def _append_items(
        self,
        lines: list[str],
        heading: str,
        items: Any,
    ) -> None:
        lines.extend(
            [
                "",
                heading,
                "-" * len(heading),
            ]
        )

        if not items:
            lines.append("None recorded.")
            return

        if isinstance(items, Mapping):
            items = [items]

        if isinstance(items, (str, bytes)):
            items = [items]

        for index, item in enumerate(items, start=1):
            if isinstance(item, Mapping):
                lines.append(f"{index}.")
                for key, value in item.items():
                    if value is None:
                        continue

                    if isinstance(
                        value,
                        (dict, list, tuple),
                    ):
                        value = json.dumps(
                            self._make_json_safe(value),
                            ensure_ascii=False,
                        )

                    lines.append(
                        f"   {self._display_name(key)}: {value}"
                    )
            else:
                lines.append(f"{index}. {item}")

    def _append_strings(
        self,
        lines: list[str],
        heading: str,
        items: Any,
    ) -> None:
        lines.extend(
            [
                "",
                heading,
                "-" * len(heading),
            ]
        )

        if not items:
            lines.append("None recorded.")
            return

        if isinstance(items, str):
            items = [items]

        for item in items:
            text = str(item).strip()
            if text:
                lines.append(f"- {text}")