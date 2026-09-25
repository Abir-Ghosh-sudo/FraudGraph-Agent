"use client";

import React, { useState, useEffect } from "react";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

interface CasePackCardProps {
  onAction: (msg: string) => void;
  onOpenModal: () => void;
}

interface ActionStates {
  freeze: "idle" | "executing" | "executed";
  sar: "idle" | "executing" | "executed";
  wire: "idle" | "executing" | "executed";
}

interface CaseView {
  case_id: string;
  title: string;
  riskLabel: string;
  evidenceCount: number;
  riskPercent: string;
  primaryTarget: string;
  evidenceItems: { id: string; color: string; label: string; detail: string }[];
}

function formatTimestamp(iso: string | undefined): string {
  if (!iso) return "—";
  return iso.slice(0, 19).replace("T", "T") + "Z";
}

function formatRiskLabel(c: Case): string {
  if (c.risk_score !== null && c.risk_score !== undefined) {
    return `RISK SCORE: ${Math.round((c.risk_score as number) * 100)}%`;
  }
  if (c.risk_level) {
    return `RISK: ${c.risk_level.toUpperCase()}`;
  }
  return `STATUS: ${c.status.toUpperCase()}`;
}

export function CasePackCard({ onAction, onOpenModal }: CasePackCardProps) {
  const [actionStates, setActionStates] = useState<ActionStates>({
    freeze: "idle",
    sar: "idle",
    wire: "idle",
  });

  const [topCase, setTopCase] = useState<CaseView | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);

  useEffect(() => {
    async function loadTopCase() {
      setLoading(true);
      setLoadError(null);
      try {
        const cases = await casesApi.list<Case[]>();
        const arr = Array.isArray(cases) ? cases : [];

        // Pick the highest risk open/investigating case
        const sorted = arr
          .filter((c) =>
            ["open", "investigating", "awaiting_approval", "escalated"].includes(c.status)
          )
          .sort((a, b) => {
            const ra = (a.risk_score as number) ?? 0;
            const rb = (b.risk_score as number) ?? 0;
            return rb - ra;
          });

        if (sorted.length > 0) {
          const c = sorted[0];
          setActiveCaseId(c.case_id);
          setTopCase({
            case_id: c.case_id.slice(0, 10).toUpperCase(),
            title: c.title.toUpperCase(),
            riskLabel: formatRiskLabel(c),
            evidenceCount: c.evidence_ids?.length ?? c.findings?.length ?? 0,
            riskPercent:
              typeof c.risk_score === "number"
                ? `${Math.round(c.risk_score * 100)}%`
                : "—",
            primaryTarget: c.customer_id
              ? `CUSTOMER: ${c.customer_id}${c.account_id ? ` · ${c.account_id}` : ""}`
              : (c.description ?? "—"),
            evidenceItems: (c.findings ?? []).slice(0, 3).map((f, i) => ({
              id: String(i + 1).padStart(2, "0"),
              color: ["var(--red)", "var(--orange)", "var(--sky)"][i] ?? "var(--mint)",
              label: `${f.title}:`,
              detail: f.description,
            })),
          });
        } else {
          // No open cases. Show an honest empty state rather than inventing one.
          setTopCase(null);
        }
      } catch (err) {
        setTopCase(null);
        setLoadError(
          err instanceof Error ? err.message : "Failed to load cases.",
        );
      } finally {
        setLoading(false);
      }
    }
    void loadTopCase();
  }, []);

  const handleAction = async (
    key: keyof ActionStates,
    label: string,
    actionType: string,
  ) => {
    if (!activeCaseId) {
      onAction(`✗ ${label} unavailable — no active case loaded.`);
      return;
    }

    setActionStates((prev) => ({ ...prev, [key]: "executing" }));
    try {
      await casesApi.addAction(activeCaseId, {
        action_id: `act_${Date.now()}`,
        action_type: actionType,
        status: "executed",
        rationale: `Analyst executed: ${label}`,
        requires_approval: false,
        result: {},
      });
      setActionStates((prev) => ({ ...prev, [key]: "executed" }));
      onAction(`✓ Action Executed: ${label}`);
    } catch (err) {
      // Surface the real failure. Never report success on a rejected request.
      setActionStates((prev) => ({ ...prev, [key]: "idle" }));
      onAction(
        `✗ ${label} failed: ${
          err instanceof Error ? err.message : "unknown error"
        }`,
      );
    }
  };

  const evidenceItems = topCase?.evidenceItems ?? [];

  return (
    <div className="brutal-card p-4 sm:p-6 bg-white relative">
      {/* Physical Tape Effect */}
      <div className="tape-strip" />

      {/* Docket Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b-[3px] border-black">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs font-black uppercase px-2 py-0.5 bg-[var(--yellow)] border-[2px] border-black">
              {loading
                ? "LOADING..."
                : topCase
                  ? `CASE DOSSIER #${topCase.case_id}`
                  : "NO ACTIVE CASE"}
            </span>
            <span className="font-mono text-xs text-[var(--muted)]">
              TIMESTAMP: {formatTimestamp(undefined)}
            </span>
          </div>
          <h2 className="font-display text-3xl sm:text-4xl uppercase tracking-tight mt-1">
            {loading ? "LOADING CASE..." : (topCase?.title ?? "NO OPEN CASES")}
          </h2>
          <p className="text-xs font-mono text-[var(--muted)]">
            PRIMARY TARGET: {loading ? "—" : (topCase?.primaryTarget ?? "—")}
          </p>
        </div>

        {/* Rubber Stamp */}
        <div className="flex flex-col items-end gap-2">
          <span className="stamp-seal">
            {loading ? "LOADING..." : (topCase?.riskLabel ?? "NO DATA")}
          </span>
          <button
            onClick={onOpenModal}
            className="btn-ghost text-xs py-1 px-3 shadow-[2px_2px_0_#050505]"
          >
            INSPECT FULL DOSSIER ↗
          </button>
        </div>
      </div>

      {loadError ? (
        <div className="mt-4 border-[3px] border-black bg-[#ff9aa2] px-4 py-2.5 shadow-[4px_4px_0_#050505]">
          <p className="font-mono text-[11px] font-bold uppercase text-black">
            Could not reach the cases API: {loadError}
          </p>
        </div>
      ) : null}

      {!loading && !loadError && !topCase ? (
        <div className="mt-4 border-[3px] border-black bg-[var(--paper)] px-4 py-3 shadow-[4px_4px_0_#050505]">
          <p className="font-mono text-[11px] font-bold uppercase text-black">
            The backend returned no open or investigating cases. Start an
            investigation to populate this docket.
          </p>
        </div>
      ) : null}

      {/* Risk Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">CASE STATUS</div>
          <div className="font-display text-2xl text-[var(--red)]">
            {loading ? "—" : topCase ? "ACTIVE" : "NONE"}
          </div>
          <div className="font-mono text-[10px] text-[var(--muted)]">
            {activeCaseId ? "Live case data" : "Backend state"}
          </div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">EVIDENCE ITEMS</div>
          <div className="font-display text-2xl text-black">
            {loading ? "—" : (topCase?.evidenceCount ?? 0)}
          </div>
          <div className="font-mono text-[10px] text-[var(--muted)]">
            Findings + evidence ids
          </div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">RISK LEVEL</div>
          <div className="font-display text-2xl text-black">
            {loading ? "—" : (topCase?.riskPercent ?? "—")}
          </div>
          <div className="font-mono text-[10px] text-[var(--muted)]">
            Model risk score
          </div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">FINDINGS</div>
          <div className="font-display text-2xl text-[var(--mint-dark)]">
            {loading ? "—" : (topCase?.evidenceItems.length ?? 0)}
          </div>
          <div className="font-mono text-[10px] text-[var(--muted)]">
            {activeCaseId ? "API findings" : "Backend state"}
          </div>
        </div>
      </div>

      {/* Evidence & Provenance List */}
      <div className="border-[3px] border-black p-4 bg-[var(--paper)] my-4">
        <div className="font-mono text-xs font-bold uppercase mb-3 flex items-center justify-between">
          <span>EVIDENCE &amp; AUDIT TRAIL</span>
          <span className="sticker sticker-mint text-[10px] py-0.5 px-1.5">
            {activeCaseId ? "LIVE DATA" : "BACKEND STATE"}
          </span>
        </div>

        {evidenceItems.length > 0 ? (
          <ul className="space-y-2 text-xs font-mono font-medium">
            {evidenceItems.map((item) => (
              <li key={item.id} className="flex items-start gap-2 bg-white border border-black p-2">
                <span className="font-bold" style={{ color: item.color }}>
                  [EVIDENCE #{item.id}]
                </span>
                <span>
                  <strong>{item.label}</strong>{" "}
                  {item.detail}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="font-mono text-[11px] text-[var(--muted)]">
            {loading
              ? "Loading evidence…"
              : "No findings recorded for this case."}
          </p>
        )}
      </div>

      {/* Next Best Action System */}
      <div className="pt-2">
        <div className="flex items-center justify-between mb-3">
          <span className="font-display text-xl uppercase tracking-tight">
            RECOMMENDED AGENT ACTIONS (HUMAN IN THE LOOP)
          </span>
          <span className="font-mono text-xs text-[var(--muted)]">APPROVAL REQUIRED</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Action 1 */}
          <button
            onClick={() => handleAction("freeze", "PROVISIONAL FREEZE ON MULE ACCOUNTS", "account_freeze")}
            disabled={actionStates.freeze !== "idle"}
            className={`${
              actionStates.freeze === "executed"
                ? "bg-black text-white cursor-default"
                : "btn-danger"
            } w-full text-xs sm:text-sm py-3 justify-center shadow-[4px_4px_0_#050505]`}
          >
            {actionStates.freeze === "executing"
              ? "[████░░░░] EXECUTING..."
              : actionStates.freeze === "executed"
              ? "✓ ACCOUNTS FROZEN"
              : "⚡ FREEZE MULE ACCOUNTS"}
          </button>

          {/* Action 2 */}
          <button
            onClick={() => handleAction("sar", "TRANSMIT FINCEN SAR REGULATORY DOCKET", "sar_report")}
            disabled={actionStates.sar !== "idle"}
            className={`${
              actionStates.sar === "executed"
                ? "bg-[var(--mint-dark)] text-black cursor-default"
                : "btn-primary"
            } w-full text-xs sm:text-sm py-3 justify-center shadow-[4px_4px_0_#050505]`}
          >
            {actionStates.sar === "executing"
              ? "[████░░░░] TRANSMITTING..."
              : actionStates.sar === "executed"
              ? "✓ SAR DOCKET SUBMITTED"
              : "FILE FINCEN SAR REPORT"}
          </button>

          {/* Action 3 */}
          <button
            onClick={() => handleAction("wire", "HOLD OUTBOUND WIRE CLEARINGS", "wire_hold")}
            disabled={actionStates.wire !== "idle"}
            className={`${
              actionStates.wire === "executed"
                ? "bg-[var(--yellow)] text-black cursor-default"
                : "btn-warning"
            } w-full text-xs sm:text-sm py-3 justify-center shadow-[4px_4px_0_#050505]`}
          >
            {actionStates.wire === "executing"
              ? "[████░░░░] HOLDING..."
              : actionStates.wire === "executed"
              ? "✓ WIRES SUSPENDED"
              : "HOLD PENDING WIRES"}
          </button>
        </div>
      </div>
    </div>
  );
}
