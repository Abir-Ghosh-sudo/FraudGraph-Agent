"use client";

import React from "react";
import Link from "next/link";
import { DefaultEvidenceWall } from "@/components/brutalist/EvidenceWall";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { DefaultTimeline } from "@/components/brutalist/Timeline";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

export default function EvidencePage() {
  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="evidence" onShowToast={() => {}} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="EVIDENCE BOARD" sticker="EVIDENCE">
          <DefaultEvidenceWall />
        </InvestigationBoard>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DefaultTimeline />
          </div>
          <div className="bg-white border-[3px] border-black p-5 shadow-[6px_6px_0_#050505] relative">
            <div className="tape-strip" />
            <span className="sticker sticker-mint text-xs">FOLLOW THE GRAPH</span>
            <h3 className="font-display text-2xl uppercase tracking-tight mt-2">
              EVIDENCE FIRST.
            </h3>
            <p className="font-mono text-xs font-semibold text-black/70 mt-2 leading-relaxed">
              Every finding is backed by graph-traversable provenance.
              No blind decisions. Every action has a reason.
            </p>
          </div>
        </div>
      </main>
      <BottomStatus />
    </div>
  );
}