"use client";

import React, { useState } from "react";

interface CasePackCardProps {
  onAction: (msg: string) => void;
  onOpenModal: () => void;
}

export function CasePackCard({ onAction, onOpenModal }: CasePackCardProps) {
  const [actionStates, setActionStates] = useState<Record<string, "idle" | "executing" | "executed">>({
    freeze: "idle",
    sar: "idle",
    wire: "idle",
  });

  const handleAction = (key: string, label: string) => {
    setActionStates((prev) => ({ ...prev, [key]: "executing" }));
    setTimeout(() => {
      setActionStates((prev) => ({ ...prev, [key]: "executed" }));
      onAction(`✓ Action Executed: ${label}`);
    }, 700);
  };

  return (
    <div className="brutal-card p-4 sm:p-6 bg-white relative">
      {/* Physical Tape Effect */}
      <div className="tape-strip" />

      {/* Docket Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b-[3px] border-black">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs font-black uppercase px-2 py-0.5 bg-[var(--yellow)] border-[2px] border-black">
              CASE DOSSIER #FG-9082
            </span>
            <span className="font-mono text-xs text-[var(--muted)]">
              TIMESTAMP: 2026-09-24T02:08:14Z
            </span>
          </div>
          <h2 className="font-display text-3xl sm:text-4xl uppercase tracking-tight mt-1">
            MULE CONVERGENCE SYNDICATE
          </h2>
          <p className="text-xs font-mono text-[var(--muted)]">
            PRIMARY TARGET: ACCOUNTS #N-8901 / #N-3319 / #N-4092 · JURISDICTION: MULTI-REGIONAL
          </p>
        </div>

        {/* Rubber Stamp */}
        <div className="flex flex-col items-end gap-2">
          <span className="stamp-seal">CONFIRMED FRAUD: 94%</span>
          <button
            onClick={onOpenModal}
            className="btn-ghost text-xs py-1 px-3 shadow-[2px_2px_0_#050505]"
          >
            INSPECT FULL DOSSIER ↗
          </button>
        </div>
      </div>

      {/* Risk Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">AT-RISK CAPITAL</div>
          <div className="font-display text-2xl text-[var(--red)]">$4,829,120</div>
          <div className="font-mono text-[10px] text-[var(--muted)]">4 Transactions Held</div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">FLAGGED VERTICES</div>
          <div className="font-display text-2xl text-black">14 ACCOUNTS</div>
          <div className="font-mono text-[10px] text-[var(--muted)]">7 Mules, 2 Shell Corps</div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">GRAPH CENTRALITY</div>
          <div className="font-display text-2xl text-black">0.89 PR</div>
          <div className="font-mono text-[10px] text-[var(--muted)]">Extreme Inbound Degree</div>
        </div>
        <div className="bg-[var(--paper)] border-[2px] border-black p-3">
          <div className="font-mono text-[11px] uppercase text-[var(--muted)]">AGENT CONFIDENCE</div>
          <div className="font-display text-2xl text-[var(--mint-dark)]">98.4%</div>
          <div className="font-mono text-[10px] text-[var(--muted)]">4/4 Nodes in Consensus</div>
        </div>
      </div>

      {/* Evidence & Provenance List */}
      <div className="border-[3px] border-black p-4 bg-[var(--paper)] my-4">
        <div className="font-mono text-xs font-bold uppercase mb-3 flex items-center justify-between">
          <span>TIGERGRAPH EVIDENCE & AUDIT TRAIL</span>
          <span className="sticker sticker-mint text-[10px] py-0.5 px-1.5">
            VERIFIED PROVENANCE
          </span>
        </div>

        <ul className="space-y-2 text-xs font-mono font-medium">
          <li className="flex items-start gap-2 bg-white border border-black p-2">
            <span className="font-bold text-[var(--red)]">[EVIDENCE #01]</span>
            <span>
              <strong>Cyclic Smurfing Topology:</strong> 4 transfers totaling $980,000 sent in rapid succession (&lt;4m interval) forming a closed loop back to offshore wallet 0x9f..4a.
            </span>
          </li>
          <li className="flex items-start gap-2 bg-white border border-black p-2">
            <span className="font-bold text-[var(--orange)]">[EVIDENCE #02]</span>
            <span>
              <strong>Synthetic Identity Match:</strong> Social Security Number collision on account #N-3319 verified against Death Master File index.
            </span>
          </li>
          <li className="flex items-start gap-2 bg-white border border-black p-2">
            <span className="font-bold text-[var(--sky)]">[EVIDENCE #03]</span>
            <span>
              <strong>Device Fingerprint Overlap:</strong> IMEI #3901-88-291 logged into 6 distinct account logins across 3 VPN exit nodes in 45 minutes.
            </span>
          </li>
        </ul>
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
            onClick={() => handleAction("freeze", "PROVISIONAL FREEZE ON 7 MULE ACCOUNTS")}
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
              ? "✓ 7 ACCOUNTS FROZEN"
              : "⚡ FREEZE 7 MULE ACCOUNTS"}
          </button>

          {/* Action 2 */}
          <button
            onClick={() => handleAction("sar", "TRANSMIT FINCEN SAR REGULATORY DOCKET")}
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
            onClick={() => handleAction("wire", "HOLD OUTBOUND WIRE CLEARINGS")}
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
              ? "✓ 4 WIRES SUSPENDED"
              : "HOLD 4 PENDING WIRES"}
          </button>
        </div>
      </div>
    </div>
  );
}
