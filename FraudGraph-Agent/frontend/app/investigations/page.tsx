"use client";

import React from "react";
import Link from "next/link";
import { AgentCognitionStream } from "@/components/brutalist/AgentCognitionStream";

export default function InvestigationsPage() {
  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <span className="sticker sticker-mint text-xs">AUTONOMOUS COGNITION</span>
            <h1 className="font-display text-4xl uppercase tracking-tight mt-1">
              ACTIVE AGENT INVESTIGATION ENGINE
            </h1>
          </div>
          <span className="status">
            <span className="status-dot-live" />
            <span>4 AGENTS IN CONSENSUS</span>
          </span>
        </div>
        <AgentCognitionStream onAction={(msg) => alert(msg)} />
      </div>
    </div>
  );
}
