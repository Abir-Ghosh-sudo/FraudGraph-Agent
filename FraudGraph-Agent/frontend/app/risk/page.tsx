"use client";

import React from "react";
import Link from "next/link";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { RiskPanel } from "@/components/brutalist/RiskPanel";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

export default function RiskPage() {
  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="risk" onShowToast={() => {}} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="RISK INTELLIGENCE" sticker="RISK">
          <RiskPanel
            score={91}
            level="HIGH"
            bankModel={78}
            mlModel={91}
            graphEvidence={85}
            historicalMatch={72}
          />
        </InvestigationBoard>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="brutal-card card-mint p-5">
            <div className="font-mono text-xs font-black uppercase">LOW RISK</div>
            <div className="font-display text-4xl mt-1">&lt; 30%</div>
            <div className="font-mono text-[11px] text-black/70 mt-1">Proceed with monitoring</div>
          </div>
          <div className="brutal-card card-yellow p-5">
            <div className="font-mono text-xs font-black uppercase">MEDIUM RISK</div>
            <div className="font-display text-4xl mt-1">30-60%</div>
            <div className="font-mono text-[11px] text-black/70 mt-1">Flag for review</div>
          </div>
          <div className="brutal-card card-pink p-5">
            <div className="font-mono text-xs font-black uppercase">HIGH / CRITICAL</div>
            <div className="font-display text-4xl mt-1">&gt; 60%</div>
            <div className="font-mono text-[11px] text-black/70 mt-1">Require human approval</div>
          </div>
        </div>
      </main>
      <BottomStatus />
    </div>
  );
}