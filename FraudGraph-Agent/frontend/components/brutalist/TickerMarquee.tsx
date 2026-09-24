"use client";

import React from "react";

export function TickerMarquee() {
  const items = [
    "CRITICAL ALERT // MULE RING #MR-9082 DETECTED",
    "14 ACCOUNTS FLAGGED ACROSS 3 JURISDICTIONS",
    "$4,829,120 PREVENTED CAPITAL DRAIN",
    "TIGERGRAPH HYBRID RETRIEVER: 99.4% PRECISION",
    "AUTONOMOUS AGENT CONSENSUS: 78.4ms LATENCY",
    "ZERO NOISE // 100% AUDITABLE PROVENANCE",
    "SYNDICATE PATTERN: CYCLIC SMURFING DETECTED",
  ];

  return (
    <div className="w-full my-4 overflow-hidden border-y-[3px] border-black bg-[var(--yellow)] shadow-[0_4px_0_#050505]">
      <div className="flex whitespace-nowrap py-2 text-black font-display text-lg sm:text-xl tracking-wider select-none animate-[marquee_30s_linear_infinite]">
        {[...items, ...items].map((text, idx) => (
          <span key={idx} className="mx-6 inline-flex items-center gap-3">
            <span className="w-2.5 h-2.5 bg-black inline-block rotate-45" />
            <span>{text}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
