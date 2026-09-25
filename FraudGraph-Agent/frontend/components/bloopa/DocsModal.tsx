"use client";

import React, { useState } from "react";

interface DocsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DocsModal({ isOpen, onClose }: DocsModalProps) {
  const [activeTab, setActiveTab] = useState<"overview" | "api" | "architecture">("overview");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs select-none">
      <div className="relative w-full max-w-2xl bg-[#f7f4ea] border-[4px] border-black p-6 sm:p-8 shadow-[12px_12px_0_#050505] max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer"
        >
          ✕
        </button>

        <div className="mb-4">
          <span className="sticker sticker-mint text-xs font-mono font-bold">
            DOCUMENTATION V2.4
          </span>
          <h2 className="font-syne font-black text-2xl sm:text-3xl text-black uppercase tracking-tight mt-1">
            FraudGraph Platform Docs
          </h2>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            Autonomous Agent Intelligence & TigerGraph Consensus for Real-Time Fraud Defense.
          </p>
        </div>

        {/* Tab switchers */}
        <div className="flex gap-2 border-b-2 border-black pb-2 mb-4 font-mono text-xs font-black uppercase">
          <button
            type="button"
            onClick={() => setActiveTab("overview")}
            className={`px-3 py-1.5 border-[2px] border-black transition-all ${
              activeTab === "overview" ? "bg-[#ffe45c] shadow-[2px_2px_0_#000]" : "bg-white"
            }`}
          >
            Overview
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("api")}
            className={`px-3 py-1.5 border-[2px] border-black transition-all ${
              activeTab === "api" ? "bg-[#ffe45c] shadow-[2px_2px_0_#000]" : "bg-white"
            }`}
          >
            Agent API
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("architecture")}
            className={`px-3 py-1.5 border-[2px] border-black transition-all ${
              activeTab === "architecture" ? "bg-[#ffe45c] shadow-[2px_2px_0_#000]" : "bg-white"
            }`}
          >
            Architecture
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="space-y-4 font-mono text-xs leading-relaxed text-neutral-800">
            <div className="bg-white border-[2.5px] border-black p-4 shadow-[3px_3px_0_#050505]">
              <h4 className="font-syne font-bold text-base text-black mb-1 uppercase">
                What is FraudGraph?
              </h4>
              <p>
                FraudGraph is an autonomous multi-agent intelligence platform powered by TigerGraph that evaluates real-time financial telemetry, discovers complex mule syndicates, and executes next-best-actions with auditable provenance.
              </p>
            </div>
            <div className="bg-white border-[2.5px] border-black p-4 shadow-[3px_3px_0_#050505]">
              <h4 className="font-syne font-bold text-base text-black mb-1 uppercase">
                Core Capabilities
              </h4>
              <ul className="list-disc pl-5 space-y-1">
                <li><strong>Hybrid Graph Retrieval:</strong> Sub-80ms GSQL queries across billions of transaction edges.</li>
                <li><strong>Cognitive Consensus:</strong> LangGraph agents debate risk and eliminate false positives.</li>
                <li><strong>FinCEN-Compliant SAR Dossiers:</strong> Automated narrative generation with interactive evidence walls.</li>
                <li><strong>Autonomous Enforcement:</strong> Instant card freeze, step-up MFA, or transaction hold.</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === "api" && (
          <div className="space-y-4 font-mono text-xs">
            <div className="bg-[#0d1117] text-neutral-200 p-4 border-[2.5px] border-black overflow-x-auto">
              <div className="text-neutral-500 mb-2">// 1. Trigger Investigation via Backend API</div>
              <pre className="text-neutral-300 text-[11px] leading-relaxed">
{`curl -X POST http://localhost:8000/api/v1/investigations \\
  -H "Content-Type: application/json" \\
  -d '{
    "account_id": "acc_mule_8829",
    "risk_threshold": 0.70,
    "hops": 3
  }'`}
              </pre>
            </div>
          </div>
        )}

        {activeTab === "architecture" && (
          <div className="space-y-3 font-mono text-xs text-neutral-800">
            <div className="bg-white border-[2.5px] border-black p-4 shadow-[3px_3px_0_#050505]">
              <h4 className="font-syne font-bold text-base text-black mb-1 uppercase">
                End-to-End Autonomous Defense Flow
              </h4>
              <div className="p-2 bg-[#f7f4ea] border border-neutral-300 space-y-1 mt-2">
                <div>[Transactions Stream] → Ingested to TigerGraph cluster</div>
                <div>[GSQL Hybrid Retriever] → Extracts high-risk subgraphs</div>
                <div>[LangGraph Agent] → Synthesizes evidence & checks policies</div>
                <div>[Policy Gate] → Executes next-best-action & exports SAR docket</div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="bg-[#b9f5cf] hover:bg-[#a1f1bc] border-[2.5px] border-black px-6 py-2.5 font-syne font-black text-xs uppercase tracking-wider shadow-[3px_3px_0_#050505] cursor-pointer"
          >
            GOT IT
          </button>
        </div>
      </div>
    </div>
  );
}
