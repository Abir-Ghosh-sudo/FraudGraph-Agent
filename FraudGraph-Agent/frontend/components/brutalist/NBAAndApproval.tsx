"use client";

import React from "react";

interface NBAPanelProps {
  action?: string;
  why?: string[];
  policy?: string;
  confidence?: number;
  onApprove?: () => void;
  onReject?: () => void;
  onMoreEvidence?: () => void;
}

export function NBARecommendation({
  action = "STEP-UP AUTH",
  why = [
    "New device detected",
    "High-risk transaction",
    "Similar historical fraud",
    "Customer identity not verified",
  ],
  policy = "R1 — Verify before block",
  confidence = 87,
  onApprove,
  onReject,
  onMoreEvidence,
}: NBAPanelProps) {
  return (
    <div className="brutal-card card-yellow p-5 sm:p-6 relative tilt-right">
      <div className="tape-strip tape-strip-right" />
      <div className="flex items-center justify-between mb-3">
        <span className="sticker sticker-pink text-xs">NEXT BEST ACTION</span>
        <span className="font-mono text-xs font-bold text-black/60">
          CONFIDENCE {confidence}%
        </span>
      </div>
      <div className="font-display text-4xl sm:text-5xl uppercase tracking-tight leading-none mb-4">
        {action}
      </div>

      <div className="border-t-[3px] border-black pt-3 mb-3">
        <div className="font-mono text-xs font-black uppercase mb-2">WHY?</div>
        <ul className="space-y-1.5">
          {why.map((item, idx) => (
            <li key={idx} className="font-mono text-xs sm:text-sm font-semibold flex items-start gap-2">
              <span className="text-[var(--pink)] mt-0.5">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t-[3px] border-black pt-3 mb-4">
        <div className="font-mono text-xs font-black uppercase">POLICY</div>
        <div className="font-mono text-sm font-bold mt-1">{policy}</div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={onApprove}
          className="btn-primary text-xs sm:text-sm py-2.5 px-5"
        >
          REQUEST VERIFICATION
        </button>
        <button
          onClick={onReject}
          className="btn-warning text-xs sm:text-sm py-2.5 px-5"
        >
          ESCALATE
        </button>
        <button
          onClick={onMoreEvidence}
          className="btn-ghost text-xs sm:text-sm py-2.5 px-5"
        >
          VIEW EVIDENCE
        </button>
      </div>
    </div>
  );
}

interface ApprovalDocumentProps {
  action?: string;
  risk?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  exposure?: string;
  policy?: string;
  onApprove?: () => void;
  onReject?: () => void;
  onMoreEvidence?: () => void;
}

export function ApprovalDocument({
  action = "BLOCK CARD",
  risk = "CRITICAL",
  exposure = "$2,840",
  policy = "L2 APPROVAL REQUIRED",
  onApprove,
  onReject,
  onMoreEvidence,
}: ApprovalDocumentProps) {
  const riskTint =
    risk === "CRITICAL"
      ? "bg-[var(--red)] text-white"
      : risk === "HIGH"
      ? "bg-[var(--pink)]"
      : risk === "MEDIUM"
      ? "bg-[var(--yellow)]"
      : "bg-[var(--mint)]";

  return (
    <div className="brutal-card card-paper p-6 sm:p-8 relative">
      <div className="tape-strip" />
      <div className="tape-strip tape-strip-right" />

      <div className="text-center mb-6">
        <span className="stamp-seal-classified text-sm font-mono font-bold px-3 py-1 border-[3px] border-black inline-block mb-3">
          HUMAN APPROVAL REQUIRED
        </span>
        <h2 className="font-display text-3xl sm:text-4xl uppercase tracking-tight">
          AUTHORIZATION DOCUMENT
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            ACTION
          </div>
          <div className="font-display text-2xl uppercase mt-1">{action}</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            RISK
          </div>
          <div
            className={`font-display text-2xl uppercase mt-1 inline-block px-3 py-1 border-[2px] border-black ${riskTint}`}
          >
            {risk}
          </div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            EXPOSURE
          </div>
          <div className="font-display text-2xl mt-1">{exposure}</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            POLICY
          </div>
          <div className="font-mono text-sm font-bold mt-1">{policy}</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 justify-center pt-4 border-t-[3px] border-black">
        <button onClick={onApprove} className="btn-primary text-sm py-3 px-6">
          APPROVE ACTION
        </button>
        <button onClick={onReject} className="btn-danger text-sm py-3 px-6">
          REJECT
        </button>
        <button onClick={onMoreEvidence} className="btn-ghost text-sm py-3 px-6">
          REQUEST MORE EVIDENCE
        </button>
      </div>
    </div>
  );
}