"use client";

import React, { useState } from "react";
import Link from "next/link";
import { DefaultEvidenceWall } from "@/components/brutalist/EvidenceWall";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { DefaultTimeline } from "@/components/brutalist/Timeline";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";
import { GraphExplorerModal } from "@/components/graph/GraphExplorerModal";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";

export default function EvidencePage() {
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [graphTarget, setGraphTarget] = useState("C12382");

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar
        activeTab="evidence"
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
              onClick={() => {
                setGraphTarget("C12382");
                setGraphModalOpen(true);
              }}
              className="bg-[#ffe45c] hover:bg-[#fed932] border-[2.5px] border-black px-3.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
            >
              EXPLORE GRAPH EVIDENCE →
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

        <InvestigationBoard heading="EVIDENCE BOARD" sticker="EVIDENCE">
          <DefaultEvidenceWall onAction={showToast} />
        </InvestigationBoard>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DefaultTimeline />
          </div>
          <div className="bg-white border-[3px] border-black p-5 shadow-[6px_6px_0_#050505] relative flex flex-col justify-between">
            <div className="tape-strip" />
            <div>
              <span className="sticker sticker-mint text-xs">FOLLOW THE GRAPH</span>
              <h3 className="font-display text-2xl uppercase tracking-tight mt-2">
                EVIDENCE FIRST.
              </h3>
              <p className="font-mono text-xs font-semibold text-black/70 mt-2 leading-relaxed">
                Every finding is backed by graph-traversable provenance.
                No blind decisions. Every action has an audit reason and policy threshold.
              </p>
            </div>
            <div className="pt-4 mt-4 border-t-2 border-neutral-200">
              <button
                type="button"
                onClick={() => {
                  setGraphTarget("N-8901");
                  setGraphModalOpen(true);
                }}
                className="w-full bg-[#b9f5cf] hover:bg-[#a1f1bc] border-[2px] border-black py-2 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
              >
                OPEN SYNDICATE TOPOLOGY →
              </button>
            </div>
          </div>
        </div>
      </main>

      <BottomStatus />

      {/* Interactive Modals */}
      <GraphExplorerModal
        isOpen={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        initialTarget={graphTarget}
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