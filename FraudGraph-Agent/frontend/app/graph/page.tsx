"use client";

import React from "react";
import Link from "next/link";
import { FraudGraphCanvas } from "@/components/brutalist/FraudGraphCanvas";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

const showToast = (msg: string) => {
  if (typeof window !== "undefined") {
    // eslint-disable-next-line no-console
    console.log(msg);
  }
};

export default function GraphPage() {
  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="graph" onShowToast={showToast} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="FRAUD RELATIONSHIP GRAPH" sticker="GRAPH">
          <FraudGraphCanvas onAction={showToast} />
        </InvestigationBoard>
      </main>
      <BottomStatus />
    </div>
  );
}