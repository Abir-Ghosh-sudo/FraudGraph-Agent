from __future__ import annotations

from pathlib import Path
from typing import Any

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "agent" / "prompts"

_PROMPT_CACHE: dict[str, str] = {}


def _load_template(name: str) -> str:
    if name in _PROMPT_CACHE:
        return _PROMPT_CACHE[name]

    path = _PROMPTS_DIR / f"{name}.txt"

    if not path.exists():
        return ""

    text = path.read_text(encoding="utf-8").strip()
    _PROMPT_CACHE[name] = text
    return text


def get_system_prompt() -> str:
    return _load_template("system")


def build_investigation_context(
    *,
    investigation_id: str,
    trigger: dict[str, Any],
    graph_summary: dict[str, Any] | None = None,
    evidence_count: int = 0,
) -> str:
    lines = [
        f"INVESTIGATION ID: {investigation_id}",
        f"TRIGGER TYPE: {trigger.get('trigger_type', 'unknown')}",
    ]

    if trigger.get("transaction_id"):
        lines.append(f"TRANSACTION: {trigger['transaction_id']}")
    if trigger.get("customer_id"):
        lines.append(f"CUSTOMER: {trigger['customer_id']}")
    if trigger.get("account_id"):
        lines.append(f"ACCOUNT: {trigger['account_id']}")
    if trigger.get("reason"):
        lines.append(f"REASON: {trigger['reason']}")

    if graph_summary:
        lines.append(
            f"GRAPH: {graph_summary.get('node_count', 0)} nodes, "
            f"{graph_summary.get('edge_count', 0)} edges"
        )

    if evidence_count:
        lines.append(f"EVIDENCE COLLECTED: {evidence_count} items")

    return "\n".join(lines)


def build_evidence_prompt(
    evidence_items: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
) -> str:
    template = _load_template("evidence")

    evidence_block = _format_evidence(evidence_items)
    pattern_block = _format_patterns(patterns)

    context = (
        f"EVIDENCE:\n{evidence_block}\n\n"
        f"DETECTED PATTERNS:\n{pattern_block}"
    )

    if template:
        return f"{template}\n\n{context}"
    return context


def build_assessment_prompt(
    *,
    investigation_context: str,
    evidence_items: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    related_cases: list[dict[str, Any]],
    risk_thresholds: dict[str, float],
) -> str:
    template = _load_template("assessment")

    evidence_block = _format_evidence(evidence_items)
    pattern_block = _format_patterns(patterns)
    cases_block = _format_related_cases(related_cases)
    threshold_block = (
        f"LOW < {risk_thresholds.get('low', 0.3):.0%}, "
        f"MEDIUM < {risk_thresholds.get('medium', 0.6):.0%}, "
        f"HIGH < {risk_thresholds.get('high', 0.85):.0%}, "
        f"else CRITICAL"
    )

    context = (
        f"INVESTIGATION:\n{investigation_context}\n\n"
        f"EVIDENCE:\n{evidence_block}\n\n"
        f"PATTERNS:\n{pattern_block}\n\n"
        f"RELATED CASES:\n{cases_block}\n\n"
        f"RISK THRESHOLDS: {threshold_block}\n\n"
        "OUTPUT FORMAT (JSON object only):\n"
        '{"risk_score": 0.0-1.0, "risk_level": "low|medium|high|critical|unknown", '
        '"confidence": 0.0-1.0, "uncertainty": 0.0-1.0, '
        '"fraud_type": "string or null", "rationale": "string"}'
    )

    if template:
        return f"{template}\n\n{context}"
    return context


def build_explanation_prompt(
    *,
    investigation_context: str,
    evidence_items: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    risk_assessment: dict[str, Any],
    decisions: list[dict[str, Any]],
    selected_action: dict[str, Any] | None,
) -> str:
    template = _load_template("explanation")

    evidence_ids = [e.get("evidence_id", "") for e in evidence_items]
    action_title = (
        selected_action.get("title", "none") if selected_action else "none"
    )

    context = (
        f"INVESTIGATION:\n{investigation_context}\n\n"
        f"RISK: {risk_assessment.get('risk_level', 'unknown')} "
        f"(score={risk_assessment.get('risk_score', 0.0):.3f}, "
        f"confidence={risk_assessment.get('confidence', 0.0):.3f})\n\n"
        f"FRAUD TYPE: {risk_assessment.get('fraud_type', 'unknown')}\n\n"
        f"EVIDENCE IDS: {', '.join(evidence_ids) or 'none'}\n\n"
        f"DETECTED PATTERNS: {_format_patterns(patterns)}\n\n"
        f"RECOMMENDED ACTION: {action_title}\n\n"
        "INSTRUCTIONS:\n"
        "- Cite evidence IDs from the provided list only.\n"
        "- Do NOT invent evidence, transactions, customers, or policies.\n"
        "- Express uncertainty where evidence is limited.\n"
        "- Distinguish inference from direct evidence.\n\n"
        "OUTPUT FORMAT (JSON object only):\n"
        '{"summary": "string", "evidence_used": ["ev_id1", ...], '
        '"reasoning_points": ["point1", ...], "uncertainty": ["reason1", ...], '
        '"action_reason": "string or null"}'
    )

    if template:
        return f"{template}\n\n{context}"
    return context


def _format_evidence(items: list[dict[str, Any]]) -> str:
    if not items:
        return "(no evidence collected)"

    lines = []
    for e in items[:20]:
        lines.append(
            f"  [{e.get('evidence_id', '?')}] "
            f"{e.get('evidence_type', '?')} / "
            f"{e.get('source_type', '?')} — "
            f"{e.get('title', '?')} "
            f"(confidence={e.get('confidence', 0.0):.2f})"
        )
    return "\n".join(lines)


def _format_patterns(patterns: list[dict[str, Any]]) -> str:
    if not patterns:
        return "(no patterns detected)"

    lines = []
    for p in patterns:
        lines.append(
            f"  [{p.get('pattern_id', '?')}] "
            f"{p.get('name', '?')} "
            f"(confidence={p.get('confidence', 0.0):.2f}) — "
            f"{p.get('rationale', '')}"
        )
    return "\n".join(lines)


def _format_related_cases(cases: list[dict[str, Any]]) -> str:
    if not cases:
        return "(no related historical cases)"

    lines = []
    for c in cases[:5]:
        lines.append(
            f"  [case={c.get('case_id', '?')}] "
            f"outcome={c.get('outcome', '?')} "
            f"similarity={c.get('similarity', 0.0):.2f}"
        )
    return "\n".join(lines)
