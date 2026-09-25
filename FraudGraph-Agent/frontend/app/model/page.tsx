"use client";

import React from "react";
import Link from "next/link";
import { ModelStatus } from "@/components/brutalist/ModelStatus";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

export default function ModelPage() {
  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="model" onShowToast={() => {}} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="THE MODEL" sticker="MODEL">
          <ModelStatus />
        </InvestigationBoard>
      </main>
      <BottomStatus />
    </div>
  );
}