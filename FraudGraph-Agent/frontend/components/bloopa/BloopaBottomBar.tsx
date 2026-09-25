"use client";

import React from "react";
import { useHealthStatus } from "@/hooks/use-dashboard";

interface BloopaBottomBarProps {
  walletConnected?: boolean;
  onOpenContract: () => void;
}

export function BloopaBottomBar({
  walletConnected = false,
  onOpenContract,
}: BloopaBottomBarProps) {
  const { health } = useHealthStatus(10000);

  const isLive = walletConnected || health.backendOnline;

  return (
    <footer className="sticky bottom-0 z-40 w-full max-w-full bg-white border-t-[3.5px] border-black shadow-[0_-4px_0_#050505] select-none">
      <div className="w-full max-w-[1340px] mx-auto px-4 sm:px-6 py-2.5 flex flex-wrap items-center justify-center sm:justify-between gap-x-4 gap-y-1.5 text-xs sm:text-sm font-mono font-bold tracking-wider">
        {/* Left Status: Connecting or Connected */}
        <div className="flex items-center gap-2 min-w-0 order-1 sm:order-none">
          {isLive ? (
            <div className="flex items-center gap-2 text-black min-w-0">
              <span className="w-2.5 h-2.5 shrink-0 rounded-full bg-[#22c55e] border border-black inline-block animate-pulse" />
              <span className="font-mono font-bold text-[11px] sm:text-xs truncate">
                CONNECTED // AGENT-09
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-neutral-600 min-w-0">
              <span className="w-2.5 h-2.5 shrink-0 rounded-full bg-neutral-300 border border-black inline-block animate-pulse" />
              <span className="font-mono font-bold text-[11px] sm:text-xs uppercase text-neutral-800 truncate">
                CONNECTING...
              </span>
            </div>
          )}
        </div>

        {/* Center: APP ID */}
        <button
          type="button"
          onClick={onOpenContract}
          className="font-mono font-black text-xs sm:text-sm text-black tracking-widest hover:text-[#4d91e8] hover:underline transition-colors flex items-center gap-1.5 cursor-pointer order-3 sm:order-none"
        >
          <span>APP</span>
          <span>764393317</span>
        </button>

        {/* Right: Network Pill */}
        <div className="border-[2px] border-black px-2.5 sm:px-3 py-0.5 bg-white text-[10px] sm:text-xs font-mono font-black uppercase text-black shadow-[2px_2px_0_#050505] whitespace-nowrap order-2 sm:order-none">
          ALGORAND TESTNET
        </div>
      </div>
    </footer>
  );
}
