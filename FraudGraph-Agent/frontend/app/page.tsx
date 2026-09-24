"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/brutalist/Navbar";
import { TickerMarquee } from "@/components/brutalist/TickerMarquee";
import { FraudGraphCanvas } from "@/components/brutalist/FraudGraphCanvas";
import { AgentCognitionStream } from "@/components/brutalist/AgentCognitionStream";
import { CasePackCard } from "@/components/brutalist/CasePackCard";
import { TransactionLedger, Transaction } from "@/components/brutalist/TransactionLedger";
import { CaseModal } from "@/components/brutalist/CaseModal";
import { ToastContainer } from "@/components/brutalist/ToastContainer";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
  };

  const handleExportDocket = () => {
    showToast("📁 Exported SAR Investigation Dossier #FG-9082 as JSON / PDF docket.");
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen paper-texture flex flex-col justify-between selection:bg-[var(--yellow)] selection:text-black">
      {/* 1. Paper Strip Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenNewCase={() => {
          showToast("🚀 Initiated autonomous TigerGraph syndicate scan across 250,000 vertices...");
          setActiveTab("cases");
        }}
        onShowToast={showToast}
      />

      {/* 2. Ticker Marquee Caution Strip */}
      <TickerMarquee />

      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-10">
        {/* =========================================================================
            SECTION: HERO POSTER (EDITORIAL & SCRAPBOOK COLLAGE)
           ========================================================================= */}
        <section className="relative pt-6 pb-10">
          {/* Scrapbook Floating Stickers (Collage Layer System) */}
          <div className="flex flex-wrap items-center gap-3 mb-6 relative z-30">
            <span className="sticker sticker-yellow">
              ● FOR AUTONOMOUS AGENTS
            </span>
            <span className="sticker sticker-mint">
              78.4ms GRAPH CONSENSUS
            </span>
            <span className="sticker sticker-pink">
              TIGERGRAPH 3.9 HYBRID RETRIEVER
            </span>
            <span className="sticker sticker-sky hidden md:inline-flex">
              ZERO FALSE POSITIVES
            </span>
          </div>

          {/* Giant Word Blocks */}
          <div className="space-y-3 relative z-20">
            <div className="flex flex-wrap items-center gap-4">
              <span className="hero-word bg-white">
                AUTONOMOUS
              </span>
              <span className="hero-word bg-[var(--mint)]">
                FRAUDGRAPH
              </span>
            </div>
            <div>
              <span className="hero-block bg-white text-black">
                CONSENSUS INTELLIGENCE
              </span>
            </div>
          </div>

          {/* Editorial Subtitle & Hero CTA Banner */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mt-8 items-start relative z-20">
            <div className="md:col-span-8 bg-white border-[3px] border-black p-5 sm:p-6 shadow-[8px_8px_0_#050505] relative">
              <div className="tape-strip" />
              <p className="font-mono text-sm sm:text-base font-semibold leading-relaxed text-black">
                A hyper-specialized autonomous multi-agent defense system executing deep TigerGraph GSQL graph traversal, topological smurfing ring discovery, and real-time human-in-the-loop consensus. Engineered for high-throughput fintech and wire clearinghouses.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-4 mt-6">
                <button
                  onClick={() => {
                    setActiveTab("graph");
                    showToast("Navigated to Interactive Graph Topology.");
                  }}
                  className="btn-primary text-sm sm:text-base py-3 px-6"
                >
                  <span>⚡ EXPLORE LIVE TOPOLOGY</span>
                  <span className="text-lg">→</span>
                </button>
                <button
                  onClick={() => {
                    setActiveTab("cases");
                    showToast("Switched to Active Case Dossier #FG-9082.");
                  }}
                  className="btn-warning text-sm sm:text-base py-3 px-6"
                >
                  <span>INSPECT ACTIVE CASE PACK</span>
                  <span>↗</span>
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="btn-secondary text-sm sm:text-base py-3 px-5"
                >
                  <span>CLASSIFIED DOSSIER</span>
                </button>
              </div>
            </div>

            {/* Collage Cutout Metric Frame */}
            <div className="md:col-span-4 bg-[var(--yellow)] border-[4px] border-black p-6 shadow-[10px_10px_0_#050505] tilt-right relative">
              <span className="font-mono text-xs font-black uppercase tracking-wider block mb-1">
                PREVENTED CAPITAL THEFT
              </span>
              <div className="font-display text-4xl sm:text-5xl text-black">
                $4,829,120
              </div>
              <div className="font-mono text-xs font-bold text-black/80 mt-2 flex items-center justify-between border-t-2 border-black pt-2">
                <span>14 MULE ACCOUNTS BLOCKED</span>
                <span className="bg-black text-white px-1.5 py-0.5 text-[10px]">● LIVE</span>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================================
            SECTION: 12-COLUMN ASYMMETRIC METRIC DASHBOARD
           ========================================================================= */}
        <section className="space-y-4">
          <div className="flex items-center justify-between border-b-[3px] border-black pb-2">
            <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
              KEY SYSTEM METRICS & TELEMETRY
            </h2>
            <span className="font-mono text-xs font-bold text-[var(--muted)]">
              UPDATED 2 SEC AGO
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Metric 1 */}
            <div className="brutal-card card-mint">
              <div className="font-mono text-xs font-black uppercase">HYBRID PRECISION</div>
              <div className="font-display text-4xl mt-1">99.4%</div>
              <p className="font-mono text-xs font-bold text-black/70 mt-1">
                TigerGraph GSQL + Vector Embeddings
              </p>
            </div>

            {/* Metric 2 */}
            <div className="brutal-card card-sky">
              <div className="font-mono text-xs font-black uppercase">CONSENSUS LATENCY</div>
              <div className="font-display text-4xl mt-1">78.4ms</div>
              <p className="font-mono text-xs font-bold text-black/70 mt-1">
                4-Node Multi-Agent Convergence
              </p>
            </div>

            {/* Metric 3 */}
            <div className="brutal-card card-yellow">
              <div className="font-mono text-xs font-black uppercase">ACTIVE SYNDICATES</div>
              <div className="font-display text-4xl mt-1">03 RINGS</div>
              <p className="font-mono text-xs font-bold text-black/70 mt-1">
                Isolated under provisional freeze
              </p>
            </div>

            {/* Metric 4 */}
            <div className="brutal-card card-pink">
              <div className="font-mono text-xs font-black uppercase">AUDIT CONVERGENCE</div>
              <div className="font-display text-4xl mt-1">100%</div>
              <p className="font-mono text-xs font-bold text-black/70 mt-1">
                Full cryptographic decision trail
              </p>
            </div>
          </div>
        </section>

        {/* =========================================================================
            SECTION: INTERACTIVE TABBED VIEWS
           ========================================================================= */}
        <section className="space-y-6">
          {/* Tab 1: Overview & Agent Stream */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <div className="lg:col-span-7">
                  <AgentCognitionStream onAction={showToast} />
                </div>
                <div className="lg:col-span-5 space-y-6">
                  <CasePackCard
                    onAction={showToast}
                    onOpenModal={() => setIsModalOpen(true)}
                  />

                  {/* Anti-Design Visual Banner Card */}
                  <div className="bg-[var(--lavender)] border-[3px] border-black p-5 shadow-[6px_6px_0_#050505] relative tilt-left">
                    <span className="sticker sticker-mint text-xs mb-2">
                      SYSTEM ARCHITECTURE
                    </span>
                    <h3 className="font-display text-2xl uppercase mt-1">
                      MULTI-AGENT HUMAN-IN-THE-LOOP
                    </h3>
                    <p className="font-mono text-xs font-semibold mt-2 leading-relaxed">
                      All high-severity capital freeze triggers require dual consensus between autonomous graph reasoning nodes and authenticated compliance officers before transmission to clearinghouse rails.
                    </p>
                  </div>
                </div>
              </div>

              {/* Mini Preview of Topology */}
              <div>
                <FraudGraphCanvas onAction={showToast} />
              </div>
            </div>
          )}

          {/* Tab 2: Graph Explorer */}
          {activeTab === "graph" && (
            <div className="space-y-6">
              <FraudGraphCanvas onAction={showToast} />
            </div>
          )}

          {/* Tab 3: Active Dossier */}
          {activeTab === "cases" && (
            <div className="space-y-6">
              <CasePackCard
                onAction={showToast}
                onOpenModal={() => setIsModalOpen(true)}
              />
              <AgentCognitionStream onAction={showToast} />
            </div>
          )}

          {/* Tab 4: Ledger */}
          {activeTab === "ledger" && (
            <div className="space-y-6">
              <TransactionLedger
                onInspect={(tx) => {
                  setSelectedTx(tx);
                  showToast(`Viewing docket for Transaction ${tx.id}`);
                  setIsModalOpen(true);
                }}
                onShowToast={showToast}
              />
            </div>
          )}

          {/* Tab 5: Benchmarks */}
          {activeTab === "benchmarks" && (
            <div className="brutal-card p-6 bg-white relative">
              <div className="tape-strip" />
              <div className="border-b-[3px] border-black pb-3 mb-6">
                <span className="sticker sticker-yellow text-xs">MODEL BENCHMARKS</span>
                <h2 className="font-display text-3xl uppercase tracking-tight mt-1">
                  FRAUDGRAPH VS. LEGACY RULE ENGINES
                </h2>
                <p className="font-mono text-xs text-[var(--muted)]">
                  Evaluated on 1,000,000 synthetic & historical AML transactions across 4 banking rails
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="border-[3px] border-black p-4 bg-[var(--paper)]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">DETECTION RECALL</div>
                  <div className="font-display text-4xl text-[var(--green)]">98.1%</div>
                  <div className="font-mono text-xs mt-2">
                    Legacy Rule Engine: <strong className="text-[var(--red)]">61.4%</strong>
                  </div>
                  <div className="mt-3 text-[11px] font-mono text-[var(--muted)]">
                    Identifies multi-hop dispersion missed by single-node threshold filters.
                  </div>
                </div>

                <div className="border-[3px] border-black p-4 bg-[var(--paper)]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">FALSE POSITIVE RATIO</div>
                  <div className="font-display text-4xl text-[var(--mint-dark)]">0.6%</div>
                  <div className="font-mono text-xs mt-2">
                    Legacy Rule Engine: <strong className="text-[var(--red)]">14.8%</strong>
                  </div>
                  <div className="mt-3 text-[11px] font-mono text-[var(--muted)]">
                    Eliminates alert fatigue with Bayesian uncertainty thresholding.
                  </div>
                </div>

                <div className="border-[3px] border-black p-4 bg-[var(--paper)]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">SETTLEMENT DELAY</div>
                  <div className="font-display text-4xl text-black">78ms</div>
                  <div className="font-mono text-xs mt-2">
                    Legacy Manual Queue: <strong className="text-[var(--red)]">4 to 24 Hours</strong>
                  </div>
                  <div className="mt-3 text-[11px] font-mono text-[var(--muted)]">
                    Autonomous agent executes verification in sub-second streaming pipelines.
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* 3. Paper Strip Bottom Footer */}
      <footer className="w-full border-t-[3px] border-black bg-white py-6 mt-12">
        <div className="container mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
          <div className="flex items-center gap-3">
            <span className="font-display text-xl">FRAUDGRAPH</span>
            <span className="text-[var(--muted)]">© 2026 AUTONOMOUS FRAUD DEFENSE AGENTS</span>
          </div>
          <div className="flex items-center gap-4 font-bold">
            <span className="hover:underline cursor-pointer" onClick={() => showToast("TigerGraph 3.9 connected via GSQL SDK.")}>
              TIGERGRAPH GSQL
            </span>
            <span>·</span>
            <span className="hover:underline cursor-pointer" onClick={() => showToast("LangGraph multi-agent pipeline active.")}>
              LANGGRAPH AGENTS
            </span>
            <span>·</span>
            <span className="hover:underline cursor-pointer" onClick={() => setIsModalOpen(true)}>
              SAR REPORT SPEC
            </span>
          </div>
        </div>
      </footer>

      {/* 4. Interactive Case Modal Docket */}
      <CaseModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onExport={handleExportDocket}
      />

      {/* 5. Snappy Brutalist Toast Notifications */}
      <ToastContainer message={toastMsg} onClear={() => setToastMsg(null)} />
    </div>
  );
}
