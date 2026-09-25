"use client";

import React from "react";
import Link from "next/link";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
  onOpenNewCase?: () => void;
  onShowToast?: (msg: string) => void;
}

export function Navbar({ activeTab = "overview", setActiveTab, onOpenNewCase, onShowToast }: NavbarProps) {
  const tabs = [
    { id: "investigations", label: "INVESTIGATIONS", href: "/investigations" },
    { id: "evidence", label: "EVIDENCE", href: "/evidence" },
    { id: "cases", label: "CASES", href: "/cases" },
    { id: "graph", label: "GRAPH", href: "/graph" },
    { id: "benchmark", label: "BENCHMARK", href: "/benchmark" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full px-4 sm:px-6 pt-4 pb-2">
      <nav
        aria-label="Main Navigation"
        className="container mx-auto bg-white border-[3px] border-black shadow-[6px_6px_0_#050505] p-3 sm:p-4 flex flex-wrap items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="cursor-pointer bg-[var(--yellow)] border-[3px] border-black px-3 py-1 font-display text-2xl sm:text-3xl tracking-tight shadow-[3px_3px_0_#050505] hover:translate-x-[1px] hover:translate-y-[1px] transition-transform"
          >
            FRAUDGRAPH
          </Link>
          <span className="sticker sticker-mint text-xs py-0.5 px-2 font-mono">
            AGENT-09
          </span>
          <div className="hidden lg:flex items-center gap-2 status">
            <span className="status-dot-live" />
            <span>SYSTEM ONLINE</span>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <Link
                key={tab.id}
                href={tab.href}
                onClick={() => setActiveTab?.(tab.id)}
                className={`font-mono text-xs sm:text-sm font-bold uppercase px-3 py-1.5 border-[2px] border-black transition-all ${
                  isActive
                    ? "bg-[var(--mint)] shadow-[3px_3px_0_#050505] translate-x-[-1px] translate-y-[-1px]"
                    : "bg-transparent hover:bg-[var(--yellow)] shadow-none"
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 status">
            <span className="status-dot-live" />
            <span>MODEL</span>
          </div>
          <button
            onClick={() => {
              onShowToast?.("⚡ Opened investigation console.");
              onOpenNewCase?.();
            }}
            className="btn-primary text-xs sm:text-sm py-2 px-4 shadow-[4px_4px_0_#050505]"
          >
            <span>OPEN CONSOLE →</span>
          </button>
        </div>
      </nav>
    </header>
  );
}