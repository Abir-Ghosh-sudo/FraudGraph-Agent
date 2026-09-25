"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useHealthStatus } from "@/hooks/use-dashboard";

interface BloopaHeaderProps {
  onOpenDossier: () => void;
  onOpenConsole: () => void;
  onOpenGraph?: () => void;
  activeCasesCount?: number;
}

export function BloopaHeader({
  onOpenDossier,
  onOpenConsole,
  onOpenGraph,
  activeCasesCount = 0,
}: BloopaHeaderProps) {
  const { health } = useHealthStatus(10000);
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: "Investigations", href: "/investigations" },
    { label: "Graph Explorer", href: "/graph", isGraph: true },
    { label: "Evidence Wall", href: "/evidence" },
    { label: "Benchmark", href: "/benchmark" },
  ];

  const handleGraphClick = (e: React.MouseEvent) => {
    if (onOpenGraph) {
      e.preventDefault();
      onOpenGraph();
      setMobileMenuOpen(false);
    }
  };

  return (
    <header className="w-full relative z-40 select-none">
      {/* 1. Top Announcement Bar (Black) */}
      <div className="w-full bg-[#050505] text-white border-b-2 border-black py-1.5 px-3 sm:px-6">
        <div className="max-w-[1440px] mx-auto flex items-center justify-between text-xs sm:text-sm font-mono font-bold tracking-tight">
          {/* Left Badges */}
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded border border-[#75d89a] text-[10px] sm:text-xs text-[#b9f5cf] font-mono font-bold">
              v2.4
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#121212] border border-[#2b2b2b] text-[10px] sm:text-xs text-white">
              <span
                className={`w-2 h-2 rounded-full ${
                  health.backendOnline ? "bg-[#22c55e] animate-pulse" : "bg-[#ff6f61]"
                }`}
              />
              <span className="font-mono tracking-wider font-extrabold text-[10px] sm:text-xs">
                {health.backendOnline ? "AGENT LIVE" : "DISPATCH STANDBY"}
              </span>
            </span>
          </div>

          {/* Center Announcement */}
          <div className="hidden md:flex items-center gap-2 font-syne tracking-wide text-xs sm:text-sm uppercase text-[#f3f4f6]">
            <span>FRAUDGRAPH V2 IS LIVE</span>
            <span className="text-[#22c55e]">💚</span>
            <span className="text-neutral-500">|</span>
            <span className="font-mono text-neutral-300 normal-case text-xs tracking-normal font-medium">
              Autonomous Agent Syndicate Defense is officially active.
            </span>
          </div>

          {/* Right Link */}
          <a
            href="#protocol-section"
            className="flex items-center gap-1 text-xs font-mono font-bold uppercase tracking-wider text-neutral-200 hover:text-white hover:underline transition-colors"
          >
            <span>ENTER V2</span>
            <span>→</span>
          </a>
        </div>
      </div>

      {/* 2. Main Brutalist Nav Container */}
      <div className="max-w-[1440px] mx-auto px-3 sm:px-6 pt-4 pb-2">
        <nav
          aria-label="FraudGraph Main Navigation"
          className="w-full bg-white border-[3px] sm:border-[4px] border-black shadow-[6px_6px_0_#050505] sm:shadow-[8px_8px_0_#050505] p-2.5 sm:p-3.5 flex items-center justify-between gap-2 sm:gap-4 flex-wrap relative"
        >
          {/* Left Brand: FG* icon + FraudGraph */}
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <Link
              href="/"
              className="flex items-center gap-2 group cursor-pointer focus:outline-none min-w-0"
            >
              <div className="w-9 h-9 sm:w-10 sm:h-10 shrink-0 bg-[#ffe45c] border-[3px] border-black flex items-center justify-center shadow-[2px_2px_0_#050505] group-hover:translate-x-[1px] group-hover:translate-y-[1px] group-hover:shadow-[1px_1px_0_#050505] transition-all">
                <span className="font-syne font-black text-base sm:text-xl text-black tracking-tighter">
                  FG*
                </span>
              </div>
              <span className="font-syne font-black text-xl sm:text-2xl lg:text-3xl text-black tracking-tight truncate min-w-0">
                FraudGraph
              </span>
            </Link>

            {/* Docs / Dossier Button */}
            <button
              type="button"
              onClick={onOpenDossier}
              className="shrink-0 ml-1 sm:ml-2 bg-white hover:bg-[#fafafa] active:translate-x-[1px] active:translate-y-[1px] border-[2px] border-black px-2 sm:px-3 py-1 text-[10px] sm:text-xs font-mono font-black uppercase tracking-wider shadow-[2px_2px_0_#050505] inline-flex items-center gap-1.5 transition-transform cursor-pointer"
            >
              <span aria-hidden="true">📄</span>
              <span className="hidden xs:inline">DOCS</span>
            </button>
          </div>

          {/* Center Navigation Links for Real App Views (Desktop) */}
          <div className="hidden lg:flex items-center gap-2">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              if (link.isGraph && onOpenGraph) {
                return (
                  <button
                    key={link.label}
                    type="button"
                    onClick={handleGraphClick}
                    className={`px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                      isActive
                        ? "bg-[#b9f5cf] border-black shadow-[2px_2px_0_#050505]"
                        : "border-transparent hover:border-black hover:bg-[#f7f4ea]"
                    }`}
                  >
                    {link.label}
                  </button>
                );
              }

              return (
                <Link
                  key={link.label}
                  href={link.href}
                  className={`px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 transition-all ${
                    isActive
                      ? "bg-[#b9f5cf] border-black shadow-[2px_2px_0_#050505]"
                      : "border-transparent hover:border-black hover:bg-[#f7f4ea]"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right Action Group */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* GRAPH Button (Section 5 Requirement: Clickable GRAPH button) */}
            <button
              type="button"
              onClick={onOpenGraph ? onOpenGraph : undefined}
              className="bg-[#f7f4ea] hover:bg-[#ffe45c] active:translate-x-[1px] active:translate-y-[1px] border-[2px] border-black px-3 py-1.5 rounded-none flex items-center gap-2 text-[11px] sm:text-xs font-mono font-black uppercase tracking-wider shadow-[2px_2px_0_#050505] cursor-pointer transition-colors"
              title="Open TigerGraph Topology Explorer"
            >
              <span
                className={`w-2.5 h-2.5 rounded-full border border-black inline-block ${
                  health.graph ? "bg-[#22c55e]" : "bg-[#ffe45c]"
                }`}
              />
              <span className="hidden xs:inline">GRAPH</span>
              <span className="hidden md:inline text-[10px] text-neutral-600 font-bold">
                {health.graph ? "ONLINE" : "STANDBY"}
              </span>
            </button>

            {/* Launch Investigation / Open Console Button */}
            <button
              type="button"
              onClick={onOpenConsole}
              className="bg-[#b9f5cf] hover:bg-[#a0f0bc] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none border-[3px] border-black px-3.5 sm:px-6 py-2 text-xs sm:text-sm font-syne font-black uppercase tracking-wider text-black shadow-[4px_4px_0_#050505] hover:shadow-[2px_2px_0_#050505] transition-all cursor-pointer flex items-center gap-2"
            >
              <span>OPEN CONSOLE</span>
              {activeCasesCount > 0 && (
                <span className="w-5 h-5 bg-black text-[#b9f5cf] rounded-full text-[10px] font-mono font-black flex items-center justify-center">
                  {activeCasesCount}
                </span>
              )}
            </button>

            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden w-9 h-9 bg-white border-[2px] border-black flex items-center justify-center font-mono font-bold text-sm shadow-[2px_2px_0_#050505] cursor-pointer"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? "✕" : "☰"}
            </button>
          </div>

          {/* Mobile Navigation Dropdown */}
          {mobileMenuOpen && (
            <div className="w-full lg:hidden pt-3 mt-2 border-t-2 border-black flex flex-col gap-2">
              {navLinks.map((link) => {
                if (link.isGraph && onOpenGraph) {
                  return (
                    <button
                      key={link.label}
                      type="button"
                      onClick={handleGraphClick}
                      className="text-left py-2 px-3 bg-[#f7f4ea] hover:bg-[#ffe45c] border border-black font-mono text-xs font-black uppercase"
                    >
                      {link.label} →
                    </button>
                  );
                }
                return (
                  <Link
                    key={link.label}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="py-2 px-3 bg-[#f7f4ea] hover:bg-[#ffe45c] border border-black font-mono text-xs font-black uppercase"
                  >
                    {link.label} →
                  </Link>
                );
              })}
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
