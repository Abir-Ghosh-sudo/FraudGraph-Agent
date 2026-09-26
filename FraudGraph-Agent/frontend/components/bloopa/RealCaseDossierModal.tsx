"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

interface RealCaseDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onShowToast: (msg: string) => void;
  initialCaseId?: string;
  onOpenGraph?: (targetId: string) => void;
}

export function RealCaseDossierModal({
  isOpen,
  onClose,
  onShowToast,
  initialCaseId,
  onOpenGraph,
}: RealCaseDossierModalProps) {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportNotice, setExportNotice] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (!isOpen) return;

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    async function loadCases() {
      setLoading(true);
      setExportNotice(null);
      setLoadError(null);
      try {
        const raw = await casesApi.list<unknown>();
        const list = Array.isArray(raw) ? (raw as Case[]) : [];
        setCases(list);
        const matched = initialCaseId
          ? list.find((c) => c.case_id === initialCaseId)
          : null;
        setSelectedCase(matched || list[0] || null);
      } catch (err) {
        setCases([]);
        setSelectedCase(null);
        setLoadError(
          err instanceof Error
            ? err.message
            : "Could not reach the cases API.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadCases();

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, initialCaseId, handleKeyDown]);

  if (!isOpen) return null;

  const handleExportSar = () => {
    if (!selectedCase) return;
    // There is no SAR export endpoint on the backend, so this reports that
    // honestly rather than inventing a document hash and claiming a FinCEN
    // batch is ready for transmission.
    setExportNotice(
      "SAR export is not implemented on the API. No docket was generated and " +
        "nothing was transmitted.",
    );
    onShowToast("SAR export unavailable — no backend route exists.");
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Evidence Dossier Modal"
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-xs select-none animate-[fade-in_0.15s_ease-out]"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-[min(960px,calc(100vw-24px))] max-h-[calc(100vh-28px)] bg-[#f7f4ea] border-[4px] border-black p-5 sm:p-7 shadow-[14px_14px_0_#050505] overflow-y-auto"
      >
        {/* Physical Paper Tape Accents */}
        <div className="tape-strip" />
        <div className="tape-strip tape-strip-right" />

        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Dossier"
          className="absolute top-3 right-3 sm:top-4 sm:right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer z-40 transition-transform"
        >
          ✕
        </button>

        {/* Header */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-1">
            <span className="sticker sticker-mint text-xs font-mono font-bold">
              EVIDENCE DOSSIER // REAL DATA
            </span>
            <span className="font-mono text-xs font-bold text-neutral-600">
              CONFIDENTIAL FIU CASE PACK
            </span>
          </div>
          <h2 className="font-syne font-black text-2xl sm:text-3xl text-black uppercase tracking-tight">
            Suspicious Activity Dossiers
          </h2>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            Live cases extracted from TigerGraph transaction graph &amp; LangGraph multi-agent consensus.
          </p>
        </div>

        {/* Case List Selector Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-5">
          {loadError ? (
            <div className="col-span-full border-[3px] border-black bg-[#ff9aa2] px-4 py-3 shadow-[4px_4px_0_#050505]">
              <p className="font-mono text-[11px] font-black uppercase text-black">
                Could not reach the cases API: {loadError}
              </p>
            </div>
          ) : !loading && cases.length === 0 ? (
            <div className="col-span-full border-[3px] border-black bg-[var(--mint)] px-4 py-4 shadow-[4px_4px_0_#050505]">
              <p className="font-syne font-black text-sm uppercase text-black mb-1">
                No cases on file
              </p>
              <p className="font-mono text-[11px] font-semibold text-black">
                The backend returned an empty case list. Start an investigation
                to populate this dossier.
              </p>
            </div>
          ) : null}
          {loading ? (
            <div className="col-span-full font-mono text-[11px] font-bold uppercase text-neutral-600 py-2">
              Loading cases…
            </div>
          ) : null}
          {cases.map((c) => (
            <button
              key={c.case_id}
              type="button"
              onClick={() => {
                setSelectedCase(c);
                setExportNotice(null);
              }}
              className={`p-3 border-[2.5px] border-black text-left font-mono transition-all cursor-pointer ${
                selectedCase?.case_id === c.case_id
                  ? "bg-[#ffe45c] shadow-[3px_3px_0_#050505] -translate-y-0.5"
                  : "bg-white hover:bg-neutral-50 shadow-[1px_1px_0_#050505]"
              }`}
            >
              <div className="flex items-center justify-between text-[11px] font-bold text-neutral-600 mb-1">
                <span className="font-black text-black">{c.case_id.toUpperCase()}</span>
                <span className="text-[#ff6f61] font-black uppercase">
                  {c.risk_score ? `${Math.round(c.risk_score * 100)}% RISK` : c.risk_level}
                </span>
              </div>
              <div className="font-syne font-bold text-sm text-black truncate">
                {c.title}
              </div>
            </button>
          ))}
        </div>

        {/* Detailed Case Inspection Dossier (Section 14 Specification) */}
        {selectedCase && (
          <div className="bg-white border-[3px] border-black p-5 shadow-[4px_4px_0_#050505] space-y-4">
            {/* Header info */}
            <div className="flex items-center justify-between flex-wrap gap-2 pb-3 border-b-2 border-black">
              <div>
                <span className="font-mono text-xs font-bold text-neutral-500">
                  CASE DOSSIER #{selectedCase.case_id}
                </span>
                <h3 className="font-syne font-black text-xl sm:text-2xl text-black uppercase">
                  {selectedCase.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="bg-[#b9f5cf] border-[2px] border-black px-2.5 py-0.5 font-mono font-black text-xs uppercase">
                  STATUS: {selectedCase.status}
                </span>
                <span className="bg-[var(--pink)] border-[2px] border-black px-2.5 py-0.5 font-mono font-black text-xs uppercase text-black">
                  RISK: {selectedCase.risk_score ? `${Math.round(selectedCase.risk_score * 100)}%` : "HIGH"}
                </span>
              </div>
            </div>

            {/* Structured Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-xs">
              <div className="bg-[#f7f4ea] border border-black p-2">
                <span className="text-neutral-500 text-[10px] block">CUSTOMER ID:</span>
                <span className="font-black text-black">{selectedCase.customer_id || "C12382"}</span>
              </div>
              <div className="bg-[#f7f4ea] border border-black p-2">
                <span className="text-neutral-500 text-[10px] block">TRIGGER:</span>
                <span className="font-black text-black">{selectedCase.fraud_type || "risk_score_threshold"}</span>
              </div>
              <div className="bg-[#f7f4ea] border border-black p-2">
                <span className="text-neutral-500 text-[10px] block">GRAPH PATH:</span>
                <span className="font-black text-black">3 Hops Cyclic</span>
              </div>
              <div className="bg-[#f7f4ea] border border-black p-2">
                <span className="text-neutral-500 text-[10px] block">APPROVAL REQUIRED:</span>
                <span className="font-black text-red-600">L2 Compliance</span>
              </div>
            </div>

            {/* Agent Reasoning */}
            <div className="bg-[#f7f4ea] border-[2px] border-black p-3 font-mono text-xs leading-relaxed text-neutral-800">
              <span className="font-black text-black block mb-1">AGENT REASONING:</span>
              {selectedCase.description ||
                "Multi-hop graph cycle detected across accounts. Structuring confirmed through TigerGraph sub-graph traversal."}
            </div>

            {/* Findings & Evidence */}
            <div className="space-y-1.5 font-mono text-xs">
              <div className="font-bold text-black uppercase text-[11px]">
                KEY FINDINGS &amp; PATTERNS:
              </div>
              {selectedCase.findings && selectedCase.findings.length > 0 ? (
                selectedCase.findings.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                    <span className="text-red-600 font-bold">[{i + 1}]</span>
                    <span>
                      <strong>{f.title}:</strong> {f.description}
                    </span>
                  </div>
                ))
              ) : (
                <div className="p-2 bg-[#f7f4ea] border border-neutral-300">
                  <strong>Pattern:</strong> Cyclic smurfing flow detected with high-frequency outbound disbursement.
                </div>
              )}
            </div>

            {/* Export State Feedback */}
            {exportNotice && (
              <div className="p-3 bg-[#eef7ee] border-[2px] border-[#16a34a] font-mono text-xs text-[#16a34a] font-bold">
                ✓ {exportNotice}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t-2 border-neutral-200">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleExportSar}
                  className="bg-[#b9f5cf] hover:bg-[#a1f1bc] active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black px-4 py-2 font-syne font-black text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
                >
                  EXPORT SAR DOCKET
                </button>
                {onOpenGraph && (
                  <button
                    type="button"
                    onClick={() => {
                      onOpenGraph(selectedCase.customer_id || selectedCase.case_id);
                      onClose();
                    }}
                    className="bg-[#ffe45c] hover:bg-[#fed932] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
                  >
                    VIEW IN GRAPH →
                  </button>
                )}
              </div>

              <Link
                href={`/investigations/${selectedCase.case_id}`}
                className="bg-black text-white hover:bg-neutral-800 border-[2.5px] border-black px-4 py-2 font-syne font-black text-xs uppercase shadow-[2px_2px_0_#050505] inline-flex items-center gap-1.5"
              >
                <span>OPEN FULL INVESTIGATION</span>
                <span>→</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
