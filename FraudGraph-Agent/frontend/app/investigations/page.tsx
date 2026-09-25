"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { AgentCognitionStream } from "@/components/brutalist/AgentCognitionStream";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { DefaultTimeline } from "@/components/brutalist/Timeline";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";
import { GraphExplorerModal } from "@/components/graph/GraphExplorerModal";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

export default function InvestigationsPage() {
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState("C12382");

  const [cases, setCases] = useState<Case[]>([]);
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
        setCases(list);
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
        activeTab="investigations"
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
            {/* Section 7 Requirement: Investigation page can open Graph Explorer */}
            <button
              type="button"
              onClick={() => {
                setSelectedTarget("C12382");
                setGraphModalOpen(true);
              }}
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

        {/* Live Multi-Agent Cognition Stream */}
        <InvestigationBoard heading="ACTIVE INVESTIGATIONS" sticker="INVESTIGATIONS">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AgentCognitionStream onAction={showToast} />
            </div>
            <div>
              <DefaultTimeline />
            </div>
          </div>
        </InvestigationBoard>

        {/* Active Investigation Cases List (Section 13 Requirement) */}
        <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[6px_6px_0_#050505]">
          <div className="flex items-center justify-between pb-3 mb-4 border-b-2 border-black flex-wrap gap-2">
            <div>
              <span className="sticker sticker-mint text-xs font-mono font-bold">LIVE DOSSIERS</span>
              <h3 className="font-display text-2xl uppercase tracking-tight mt-1">
                EVALUATED CASES &amp; NEXT-BEST-ACTIONS
              </h3>
            </div>
            <span className="font-mono text-xs text-neutral-500 font-semibold">
              Select any card to inspect full agent trail
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(cases.length > 0
              ? cases
              : [
                  {
                    case_id: "HHG-001",
                    status: "investigating",
                    risk_score: 0.61,
                    customer_id: "C12382",
                    fraud_type: "risk_score_anomaly",
                    title: "Regional Billing Anomaly",
                    evidence_ids: ["ev_1", "ev_2"],
                    nba: "VERIFY_WITH_CUSTOMER",
                  },
                  {
                    case_id: "HHG-002",
                    status: "open",
                    risk_score: 0.79,
                    customer_id: "C11891",
                    fraud_type: "online_velocity_burst",
                    title: "High Value Online Charge",
                    evidence_ids: ["ev_3"],
                    nba: "STEP_UP_AUTH",
                  },
                  {
                    case_id: "HHG-003",
                    status: "open",
                    risk_score: 0.85,
                    customer_id: "C08623",
                    fraud_type: "customer_dispute",
                    title: "Unauthorized Charge Dispute",
                    evidence_ids: ["ev_4", "ev_5"],
                    nba: "BLOCK_CARD",
                  },
                  {
                    case_id: "HHG-004",
                    status: "awaiting_approval",
                    risk_score: 0.94,
                    customer_id: "C08106",
                    fraud_type: "mule_syndicate",
                    title: "3-Hop Smurfing Ring",
                    evidence_ids: ["ev_6", "ev_7", "ev_8"],
                    nba: "FREEZE_ACCOUNT_24H",
                  },
                ]
            ).map((c: any) => (
              <div
                key={c.case_id}
                className="bg-[#f7f4ea] border-[2.5px] border-black p-4 shadow-[4px_4px_0_#050505] hover:shadow-[6px_6px_0_#050505] hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-2">
                    <span className="font-black bg-black text-white px-2 py-0.5">
                      {c.case_id}
                    </span>
                    <span className="font-black text-red-600 bg-red-100 px-1.5 py-0.5 border border-red-300">
                      {c.risk_score ? `${Math.round(c.risk_score * 100)}% RISK` : "HIGH"}
                    </span>
                  </div>

                  <h4 className="font-syne font-bold text-base text-black mb-1 line-clamp-1">
                    {c.title}
                  </h4>

                  <div className="font-mono text-xs text-neutral-600 space-y-1 my-3 bg-white border border-neutral-300 p-2">
                    <div><strong>CUSTOMER:</strong> {c.customer_id}</div>
                    <div><strong>TRIGGER:</strong> {c.fraud_type}</div>
                    <div><strong>STATUS:</strong> {c.status.toUpperCase()}</div>
                    <div><strong>EVIDENCE COUNT:</strong> {c.evidence_ids?.length || 2} items</div>
                    <div className="text-black font-black pt-1 border-t border-dashed border-neutral-200">
                      <strong>NBA:</strong> {c.nba || "STEP_UP_AUTH"}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-neutral-300">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedTarget(c.customer_id || c.case_id);
                      setGraphModalOpen(true);
                    }}
                    className="flex-1 bg-[#ffe45c] hover:bg-[#fed932] border-[2px] border-black py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
                  >
                    GRAPH →
                  </button>
                  <Link
                    href={`/investigations/${c.case_id}`}
                    className="flex-1 bg-black text-white hover:bg-neutral-800 border-[2px] border-black py-1.5 text-center font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505]"
                  >
                    DETAILS →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      <BottomStatus />

      {/* Interactive Modals */}
      <GraphExplorerModal
        isOpen={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        initialTarget={selectedTarget}
        onShowToast={showToast}
      />

      <ProtocolModal
        isOpen={consoleOpen}
        onClose={() => setConsoleOpen(false)}
        onSuccessToast={showToast}
      />

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