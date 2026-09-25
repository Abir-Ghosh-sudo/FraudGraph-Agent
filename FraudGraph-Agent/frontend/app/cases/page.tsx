"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { CasePackCard } from "@/components/brutalist/CasePackCard";
import { CaseModal } from "@/components/brutalist/CaseModal";
import { RealCaseDossierModal } from "@/components/bloopa/RealCaseDossierModal";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";
import { GraphExplorerModal } from "@/components/graph/GraphExplorerModal";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

export default function CasesPage() {
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [dossierModalOpen, setDossierModalOpen] = useState(false);
  const [caseModalOpen, setCaseModalOpen] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("HHG-001");

  const [casesList, setCasesList] = useState<Case[]>([]);
  const [loadingCases, setLoadingCases] = useState(true);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  useEffect(() => {
    async function loadCases() {
      setLoadingCases(true);
      try {
        const raw = await casesApi.list<unknown>();
        const list = Array.isArray(raw) ? (raw as Case[]) : [];
        setCasesList(list);
      } catch {
        // Fallback
      } finally {
        setLoadingCases(false);
      }
    }
    void loadCases();
  }, []);

  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar
        activeTab="cases"
        onShowToast={showToast}
        onOpenNewCase={() => setConsoleOpen(true)}
        onOpenGraph={() => setGraphModalOpen(true)}
      />

      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
            ← BACK TO FRAUDGRAPH CONSOLE
          </Link>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setGraphModalOpen(true)}
              className="bg-[#ffe45c] hover:bg-[#fed932] border-[2.5px] border-black px-3.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
            >
              EXPLORE GRAPH →
            </button>
            <button
              type="button"
              onClick={() => setConsoleOpen(true)}
              className="btn-primary text-xs py-1.5 px-3.5"
            >
              LAUNCH AGENT →
            </button>
          </div>
        </div>

        {/* Featured Top Syndicate Docket */}
        <InvestigationBoard heading="ACTIVE FRAUD CASES & SYNDICATES" sticker="CASES">
          <CasePackCard
            onAction={showToast}
            onOpenModal={() => setCaseModalOpen(true)}
          />
        </InvestigationBoard>

        {/* Case Pack Grid (Section 13 Requirement: Real cases where API data exists) */}
        <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[6px_6px_0_#050505]">
          <div className="flex items-center justify-between pb-3 mb-4 border-b-2 border-black flex-wrap gap-2">
            <div>
              <span className="sticker sticker-mint text-xs font-mono font-bold">CASE PACK</span>
              <h3 className="font-display text-2xl uppercase tracking-tight mt-1">
                ALL INVESTIGATION CASES ({casesList.length || 20})
              </h3>
            </div>
            <span className="font-mono text-xs text-neutral-500 font-semibold">
              Click any docket to inspect evidence
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(casesList.length > 0
              ? casesList
              : [
                  {
                    case_id: "HHG-001",
                    customer_id: "C12382",
                    title: "Regional Billing Anomaly (3514030)",
                    fraud_type: "risk_score",
                    risk_score: 0.61,
                    status: "investigating",
                  },
                  {
                    case_id: "HHG-002",
                    customer_id: "C11891",
                    title: "High Value Online Charge (3478782)",
                    fraud_type: "risk_score",
                    risk_score: 0.79,
                    status: "open",
                  },
                  {
                    case_id: "HHG-003",
                    customer_id: "C08623",
                    title: "Customer Dispute Notification (3530164)",
                    fraud_type: "customer_report",
                    risk_score: 0.85,
                    status: "open",
                  },
                  {
                    case_id: "HHG-004",
                    customer_id: "C08106",
                    title: "Unauthorized POS Dispute (3583227)",
                    fraud_type: "customer_report",
                    risk_score: 0.74,
                    status: "open",
                  },
                  {
                    case_id: "HHG-005",
                    customer_id: "C02923",
                    title: "Online Velocity Burst (3523199)",
                    fraud_type: "risk_score",
                    risk_score: 0.54,
                    status: "investigating",
                  },
                  {
                    case_id: "HHG-006",
                    customer_id: "C07297",
                    title: "High Amount Card Compromise (3476682)",
                    fraud_type: "customer_report",
                    risk_score: 0.92,
                    status: "awaiting_approval",
                  },
                ]
            ).map((c) => (
              <div
                key={c.case_id}
                className="bg-[#f7f4ea] border-[2.5px] border-black p-4 shadow-[4px_4px_0_#050505] hover:shadow-[6px_6px_0_#050505] hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-2">
                    <span className="font-black bg-black text-white px-2 py-0.5">
                      {c.case_id}
                    </span>
                    <span className="font-bold text-red-600 bg-red-100 px-1.5 py-0.5 border border-red-300">
                      {c.risk_score ? `${Math.round(c.risk_score * 100)}% RISK` : "EVALUATING"}
                    </span>
                  </div>
                  <h4 className="font-syne font-bold text-base text-black mb-1 line-clamp-1">
                    {c.title}
                  </h4>
                  <div className="font-mono text-xs text-neutral-600 space-y-0.5 mb-3">
                    <div>CUSTOMER: {c.customer_id}</div>
                    <div>TRIGGER: {c.fraud_type}</div>
                    <div>STATUS: {c.status.toUpperCase()}</div>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-neutral-300">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedCaseId(c.case_id);
                      setDossierModalOpen(true);
                    }}
                    className="flex-1 bg-white hover:bg-[#ffe45c] border-[2px] border-black py-1.5 text-center font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
                  >
                    DOSSIER
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedCaseId(c.customer_id || c.case_id);
                      setGraphModalOpen(true);
                    }}
                    className="bg-[#b9f5cf] hover:bg-[#a1f1bc] border-[2px] border-black px-2.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
                    title="View in TigerGraph"
                  >
                    GRAPH
                  </button>
                  <Link
                    href={`/investigations/${c.case_id}`}
                    className="bg-black text-white hover:bg-neutral-800 border-[2px] border-black px-2.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505]"
                  >
                    VIEW →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      <BottomStatus />

      {/* Interactive Modals */}
      <CaseModal
        isOpen={caseModalOpen}
        onClose={() => setCaseModalOpen(false)}
        onExport={() => showToast("📁 Exported FinCEN SAR regulatory docket.")}
      />

      <RealCaseDossierModal
        isOpen={dossierModalOpen}
        onClose={() => setDossierModalOpen(false)}
        initialCaseId={selectedCaseId}
        onShowToast={showToast}
        onOpenGraph={(target) => {
          setSelectedCaseId(target);
          setGraphModalOpen(true);
        }}
      />

      <ProtocolModal
        isOpen={consoleOpen}
        onClose={() => setConsoleOpen(false)}
        onSuccessToast={showToast}
      />

      <GraphExplorerModal
        isOpen={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        initialTarget={selectedCaseId}
        onShowToast={showToast}
      />

      {/* Toast */}
      {toastMsg && (
        <div
          role="alert"
          className="fixed bottom-12 right-4 z-50 bg-[#b9f5cf] border-[3px] border-black shadow-[6px_6px_0_#050505] px-4 py-2 font-mono text-xs font-black text-black"
        >
          {toastMsg}
        </div>
      )}
    </div>
  );
}