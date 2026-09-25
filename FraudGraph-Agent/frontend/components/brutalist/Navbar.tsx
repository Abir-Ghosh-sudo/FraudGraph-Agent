"use client";

import React, { useState } from "react";
import Link from "next/link";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
  onOpenNewCase?: () => void;
  onOpenGraph?: () => void;
  onShowToast?: (msg: string) => void;
}

export function Navbar({
  activeTab = "overview",
  setActiveTab,
  onOpenNewCase,
  onOpenGraph,
  onShowToast,
}: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { id: "investigations", label: "INVESTIGATIONS", href: "/investigations" },
    { id: "evidence", label: "EVIDENCE", href: "/evidence" },
    { id: "cases", label: "CASES", href: "/cases" },
    { id: "graph", label: "GRAPH", href: "/graph" },
    { id: "benchmark", label: "BENCHMARK", href: "/benchmark" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full px-3 sm:px-6 pt-3 sm:pt-4 pb-2 select-none">
      <nav
        aria-label="Main Navigation"
        className="max-w-[1440px] mx-auto bg-white border-[3px] border-black shadow-[6px_6px_0_#050505] p-2.5 sm:p-4 flex flex-wrap items-center justify-between gap-3"
      >
        {/* Left: Brand */}
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/"
            className="cursor-pointer bg-[var(--yellow)] border-[2.5px] sm:border-[3px] border-black px-2.5 sm:px-3 py-1 font-display text-xl sm:text-2xl md:text-3xl tracking-tight shadow-[3px_3px_0_#050505] hover:translate-x-[1px] hover:translate-y-[1px] transition-transform"
          >
            FRAUDGRAPH
          </Link>
          <span className="sticker sticker-mint text-[10px] sm:text-xs py-0.5 px-1.5 sm:px-2 font-mono">
            AGENT-09
          </span>
          <div className="hidden lg:flex items-center gap-2 status">
            <span className="status-dot-live" />
            <span>SYSTEM ONLINE</span>
          </div>
        </div>

        {/* Center: Tabs (Desktop) */}
        <div className="hidden md:flex items-center gap-1.5 sm:gap-2 flex-wrap">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <Link
                key={tab.id}
                href={tab.href}
                onClick={() => setActiveTab?.(tab.id)}
                className={`font-mono text-xs sm:text-sm font-bold uppercase px-2.5 sm:px-3 py-1.5 border-[2px] border-black transition-all ${
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

        {/* Right: Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {onOpenGraph && (
            <button
              type="button"
              onClick={onOpenGraph}
              className="bg-[#f7f4ea] hover:bg-[#ffe45c] border-[2px] border-black px-2.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
            >
              GRAPH
            </button>
          )}

          <button
            type="button"
            onClick={() => {
              onShowToast?.("⚡ Opened autonomous investigation console.");
              onOpenNewCase?.();
            }}
            className="btn-primary text-xs sm:text-sm py-1.5 sm:py-2 px-3 sm:px-4 shadow-[4px_4px_0_#050505] cursor-pointer"
          >
            <span>CONSOLE →</span>
          </button>

          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden w-8 h-8 bg-white border-[2px] border-black flex items-center justify-center font-mono font-bold text-sm shadow-[2px_2px_0_#050505] cursor-pointer"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? "✕" : "☰"}
          </button>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="w-full md:hidden pt-3 mt-1 border-t-2 border-black flex flex-col gap-1.5">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <Link
                  key={tab.id}
                  href={tab.href}
                  onClick={() => {
                    setActiveTab?.(tab.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`py-1.5 px-3 font-mono text-xs font-black uppercase border border-black ${
                    isActive ? "bg-[var(--mint)]" : "bg-[#f7f4ea] hover:bg-[var(--yellow)]"
                  }`}
                >
                  {tab.label} →
                </Link>
              );
            })}
          </div>
        )}
      </nav>
    </header>
  );
}