"use client";

import React from "react";
import Link from "next/link";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenNewCase: () => void;
  onShowToast: (msg: string) => void;
}

export function Navbar({ activeTab, setActiveTab, onOpenNewCase, onShowToast }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 w-full px-4 sm:px-6 pt-4 pb-2">
      <nav
        aria-label="Main Navigation"
        className="container mx-auto bg-white border-[3px] border-black shadow-[6px_6px_0_#050505] p-3 sm:p-4 flex flex-wrap items-center justify-between gap-4"
      >
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <div
            onClick={() => setActiveTab("overview")}
            className="cursor-pointer bg-[var(--yellow)] border-[3px] border-black px-3 py-1 font-display text-2xl sm:text-3xl tracking-tight shadow-[3px_3px_0_#050505] hover:translate-x-[1px] hover:translate-y-[1px] transition-transform"
          >
            FRAUDGRAPH
          </div>
          <span className="sticker sticker-mint text-xs py-0.5 px-2 font-mono">
            AGENT-09
          </span>
          <div className="hidden lg:flex items-center gap-2 status">
            <span className="status-dot-live" />
            <span>TIGERGRAPH 3.9 : LIVE</span>
          </div>
        </div>

        {/* Center: Nav Tabs */}
        <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
          {[
            { id: "overview", label: "01. OVERVIEW" },
            { id: "graph", label: "02. GRAPH EXPLORER" },
            { id: "cases", label: "03. ACTIVE DOSSIER" },
            { id: "ledger", label: "04. LEDGER" },
            { id: "benchmarks", label: "05. BENCHMARKS" },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`font-mono text-xs sm:text-sm font-bold uppercase px-3 py-1.5 border-[2px] border-black transition-all ${
                  isActive
                    ? "bg-[var(--mint)] shadow-[3px_3px_0_#050505] translate-x-[-1px] translate-y-[-1px]"
                    : "bg-transparent hover:bg-[var(--yellow)] shadow-none"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              onShowToast("⚡ TigerGraph hybrid retriever synced (1,489 vertices updated)");
            }}
            className="btn-ghost hidden sm:inline-flex text-xs py-2 px-3"
            title="Sync graph cache"
          >
            <span className="font-mono">SYNC GRAPH</span>
          </button>
          <button
            onClick={onOpenNewCase}
            className="btn-primary text-xs sm:text-sm py-2 px-4 shadow-[4px_4px_0_#050505]"
          >
            <span>+ TRIGGER AGENT</span>
          </button>
        </div>
      </nav>
    </header>
  );
}
