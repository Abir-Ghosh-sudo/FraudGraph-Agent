"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FraudGraphCanvas } from "@/components/brutalist/FraudGraphCanvas";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";

export default function GraphPage() {
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [consoleOpen, setConsoleOpen] = useState(false);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar
        activeTab="graph"
        onShowToast={showToast}
        onOpenNewCase={() => setConsoleOpen(true)}
      />

      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
            ← BACK TO FRAUDGRAPH CONSOLE
          </Link>
          <div className="flex items-center gap-2">
            <Link
              href="/investigations"
              className="bg-white hover:bg-neutral-100 border-[2.5px] border-black px-3.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505]"
            >
              INVESTIGATIONS →
            </Link>
            <button
              type="button"
              onClick={() => setConsoleOpen(true)}
              className="btn-primary text-xs py-1.5 px-3.5"
            >
              OPEN AGENT CONSOLE →
            </button>
          </div>
        </div>

        <InvestigationBoard heading="FRAUD RELATIONSHIP GRAPH" sticker="GRAPH">
          <FraudGraphCanvas onAction={showToast} />
        </InvestigationBoard>
      </main>

      <BottomStatus />

      {/* Protocol Modal */}
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