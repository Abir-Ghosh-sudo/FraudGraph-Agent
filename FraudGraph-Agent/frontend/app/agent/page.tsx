"use client";

import React from "react";
import Link from "next/link";
import { TerminalBlock } from "@/components/brutalist/TerminalBlock";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { AgentCognitionStream } from "@/components/brutalist/AgentCognitionStream";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

export default function AgentPage() {
  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="agent" onShowToast={() => {}} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="LIVE AGENT TERMINAL" sticker="AGENT">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TerminalBlock />
            <AgentCognitionStream onAction={() => {}} />
          </div>
        </InvestigationBoard>
      </main>
      <BottomStatus />
    </div>
  );
}