"use client";

import React from "react";

interface CaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: () => void;
}

export function CaseModal({ isOpen, onClose, onExport }: CaseModalProps) {
  if (!isOpen) return null;

  return (
    <div className="brutal-modal-backdrop" onClick={onClose}>
      <div
        className="brutal-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* Physical Paper Tape Top Corner */}
        <div className="tape-strip" />
        <div className="tape-strip tape-strip-right" />

        {/* Modal Top Bar */}
        <div className="flex items-start justify-between pb-3 border-b-[3px] border-black">
          <div>
            <div className="flex items-center gap-2">
              <span className="stamp-seal-classified text-xs font-mono font-bold px-2 py-0.5 border-[2px] border-black">
                CLASSIFIED FIU DOSSIER
              </span>
              <span className="font-mono text-xs font-bold text-[var(--muted)]">
                REF #FG-9082-US-EU
              </span>
            </div>
            <h2 className="font-display text-3xl sm:text-4xl uppercase tracking-tight mt-1">
              INVESTIGATION PACK: SMURFING RING ALPHA
            </h2>
          </div>

          <button
            onClick={onClose}
            className="w-9 h-9 bg-black text-white font-mono font-black text-lg flex items-center justify-center hover:bg-[var(--red)] transition-colors border-[2px] border-black"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="my-4 space-y-4 font-mono text-xs sm:text-sm">
          {/* Executive Summary */}
          <div className="bg-white border-[2px] border-black p-3.5 shadow-[3px_3px_0_#050505]">
            <div className="font-bold text-xs uppercase text-[var(--muted)] mb-1">
              EXECUTIVE SYNOPSIS
            </div>
            <p className="leading-relaxed">
              Automated graph neural intelligence detected an orchestrated 3-hop money laundering syndicate across 14 bank vertices. Funds were structured into sub-$10,000 increments to circumvent CTR thresholds before consolidating through offshore shell company entities and cryptocurrency mixer bridges.
            </p>
          </div>

          {/* Key Findings Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-[var(--paper)] border-[2px] border-black p-3">
              <div className="font-bold text-[11px] uppercase text-[var(--muted)]">PRIMARY DISPERSION NODE</div>
              <div className="font-display text-xl">ACCOUNT #N-8901</div>
              <p className="text-[11px] text-[var(--muted)] mt-1">
                Outbound velocity: 7 transfers / 4 mins. Destination: Shell Corp #N-4092.
              </p>
            </div>
            <div className="bg-[var(--paper)] border-[2px] border-black p-3">
              <div className="font-bold text-[11px] uppercase text-[var(--muted)]">SYNTHETIC IDENTITY LINK</div>
              <div className="font-display text-xl">SSN #***-**-3319</div>
              <p className="text-[11px] text-[var(--muted)] mt-1">
                Colliding identity vector. Death Master File match confirmed by agent.
              </p>
            </div>
          </div>

          {/* TigerGraph Query Code Block */}
          <div className="bg-black text-[var(--mint)] p-3 border-[2px] border-black overflow-x-auto text-[11px] font-mono leading-relaxed">
            <div className="text-[var(--yellow)] mb-1">// TIGERGRAPH GSQL ENGINE RUNTIME QUERY:</div>
            <code>
              INTERPRET QUERY (VERTEX&lt;Account&gt; root) FOR GRAPH FraudNetwork &#123;<br />
              &nbsp;&nbsp;Orch = SELECT t FROM root:s -(TRANSFER:e)- Account:t<br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WHERE e.amount &gt; 50000 AND e.timestamp &gt; now() - 3600<br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ACCUM @@cycle_weight += e.amount;<br />
              &nbsp;&nbsp;PRINT Orch, @@cycle_weight;<br />
              &#125;
            </code>
          </div>

          {/* Audit Signatures */}
          <div className="bg-white border-[2px] border-black p-3 text-xs">
            <div className="font-bold uppercase text-[var(--muted)] mb-1.5">
              CONSENSUS AUDIT TRAIL & VERIFICATION HASH
            </div>
            <div className="flex flex-wrap gap-2 text-[11px]">
              <span className="bg-[var(--paper)] border border-black px-2 py-0.5">
                AGENT: TigerGraph-Retrieval-v2.1
              </span>
              <span className="bg-[var(--paper)] border border-black px-2 py-0.5">
                HASH: sha256:8f4c2199b4a...
              </span>
              <span className="bg-[var(--mint)] border border-black px-2 py-0.5 font-bold">
                STATUS: HUMAN VERIFICATION PENDING
              </span>
            </div>
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t-[3px] border-black">
          <button onClick={onClose} className="btn-ghost text-xs py-2 px-4">
            CLOSE DOSSIER
          </button>
          <button onClick={onExport} className="btn-primary text-xs py-2 px-5">
            DOWNLOAD SAR AUDIT DOCKET (.JSON / .PDF)
          </button>
        </div>
      </div>
    </div>
  );
}
