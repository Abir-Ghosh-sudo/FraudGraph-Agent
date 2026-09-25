"use client";

import React from "react";
import Link from "next/link";
import { useHealthStatus } from "@/hooks/use-dashboard";

interface BloopaHeaderProps {
  onOpenDossier: () => void;
  onOpenConsole: () => void;
  activeCasesCount?: number;
}

export function BloopaHeader({
  onOpenDossier,
  onOpenConsole,
  activeCasesCount = 0,
}: BloopaHeaderProps) {
  const { health } = useHealthStatus(10000);

  return (
    <header className="w-full relative z-40 select-none">
      {/* 1. Top Announcement Bar (Black) */}
      <div className="w-full bg-[#050505] text-white border-b-2 border-black py-1.5 px-3 sm:px-6">
        <div className="max-w-[1340px] mx-auto flex items-center justify-between text-xs sm:text-sm font-mono font-bold tracking-tight">
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
      <div className="max-w-[1340px] mx-auto px-3 sm:px-6 pt-4 pb-2">
        <nav
          aria-label="FraudGraph Main Navigation"
          className="w-full bg-white border-[3px] sm:border-[4px] border-black shadow-[6px_6px_0_#050505] sm:shadow-[8px_8px_0_#050505] p-2.5 sm:p-3.5 flex items-center justify-between gap-2 sm:gap-4 flex-wrap"
        >
          {/* Left Brand: FG* icon + FraudGraph */}
          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/"
              className="flex items-center gap-2 group cursor-pointer focus:outline-none"
            >
              {/* Yellow Square FG* */}
              <div className="w-9 h-9 sm:w-10 sm:h-10 bg-[#ffe45c] border-[3px] border-black flex items-center justify-center shadow-[2px_2px_0_#050505] group-hover:translate-x-[1px] group-hover:translate-y-[1px] group-hover:shadow-[1px_1px_0_#050505] transition-all">
                <span className="font-syne font-black text-lg sm:text-xl text-black tracking-tighter">
                  FG*
                </span>
              </div>
              {/* Brand text */}
              <span className="font-syne font-black text-2xl sm:text-3xl text-black tracking-tight">
                FraudGraph
              </span>
            </Link>

            {/* Docs / Dossier Button */}
            <button
              type="button"
              onClick={onOpenDossier}
              className="ml-1 sm:ml-2 bg-white hover:bg-[#fafafa] active:translate-x-[1px] active:translate-y-[1px] border-[2px] border-black px-2.5 sm:px-3 py-1 text-xs font-mono font-black uppercase tracking-wider shadow-[2px_2px_0_#050505] inline-flex items-center gap-1.5 transition-transform cursor-pointer"
            >
              <span>📄</span>
              <span>DOCS</span>
            </button>
          </div>

          {/* Center Navigation Links for Real App Views */}
          <div className="hidden lg:flex items-center gap-2">
            <Link
              href="/investigations"
              className="px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 border-transparent hover:border-black hover:bg-[#f7f4ea] transition-all"
            >
              Investigations
            </Link>
            <Link
              href="/graph"
              className="px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 border-transparent hover:border-black hover:bg-[#f7f4ea] transition-all"
            >
              Graph Explorer
            </Link>
            <Link
              href="/evidence"
              className="px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 border-transparent hover:border-black hover:bg-[#f7f4ea] transition-all"
            >
              Evidence Wall
            </Link>
            <Link
              href="/benchmark"
              className="px-2.5 py-1 text-xs font-mono font-bold uppercase border-2 border-transparent hover:border-black hover:bg-[#f7f4ea] transition-all"
            >
              Benchmark
            </Link>
          </div>

          {/* Right Action Group */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* TigerGraph Network Status Pill */}
            <div className="bg-[#f7f4ea] border-[2px] border-black px-3 py-1.5 rounded-none flex items-center gap-2 text-[11px] sm:text-xs font-mono font-bold uppercase tracking-wider shadow-[2px_2px_0_#050505]">
              <span
                className={`w-2.5 h-2.5 rounded-full border border-black inline-block ${
                  health.graph ? "bg-[#9cc9ff]" : "bg-[#ffe45c]"
                }`}
              />
              <span className="hidden xs:inline">
                {health.graph ? "TIGERGRAPH ONLINE" : "GRAPH CLUSTER"}
              </span>
              <span className="xs:hidden">GRAPH</span>
            </div>

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
          </div>
        </nav>
      </div>
    </header>
  );
}
