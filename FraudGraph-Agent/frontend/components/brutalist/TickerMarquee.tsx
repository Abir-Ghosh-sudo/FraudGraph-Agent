"use client";

import React, { useEffect, useState } from "react";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

const FALLBACK_ITEMS = [
  "CRITICAL ALERT // MULE RING #MR-9082 DETECTED",
  "14 ACCOUNTS FLAGGED ACROSS 3 JURISDICTIONS",
  "$4,829,120 PREVENTED CAPITAL DRAIN",
  "TIGERGRAPH HYBRID RETRIEVER: 99.4% PRECISION",
  "AUTONOMOUS AGENT CONSENSUS: 78.4ms LATENCY",
  "ZERO NOISE // 100% AUDITABLE PROVENANCE",
  "SYNDICATE PATTERN: CYCLIC SMURFING DETECTED",
];

export function TickerMarquee() {
  const [items, setItems] = useState<string[]>(FALLBACK_ITEMS);

  useEffect(() => {
    async function buildTicker() {
      try {
        const cases = await casesApi.list<Case[]>();
        const arr = Array.isArray(cases) ? cases : [];

        if (arr.length === 0) return;

        const dynamicItems: string[] = [];

        // Add case-based ticker items
        for (const c of arr.slice(0, 5)) {
          const score = c.risk_score != null ? Math.round((c.risk_score as number) * 100) : null;
          const status = c.status.replace("_", " ").toUpperCase();
          if (score !== null && score > 70) {
            dynamicItems.push(`⚠ HIGH RISK // ${c.title.slice(0, 35).toUpperCase()} [${score}% RISK]`);
          } else {
            dynamicItems.push(`CASE ${c.case_id.slice(0, 8).toUpperCase()} · ${status} · ${c.title.slice(0, 30).toUpperCase()}`);
          }
        }

        // Count stats
        const active = arr.filter((c) =>
          ["open", "investigating", "awaiting_approval", "escalated"].includes(c.status)
        ).length;
        const high = arr.filter((c) => c.risk_level === "high").length;
        const resolved = arr.filter((c) => c.status === "resolved").length;

        if (active > 0) dynamicItems.push(`${active} ACTIVE CASES IN INVESTIGATION PIPELINE`);
        if (high > 0) dynamicItems.push(`${high} HIGH-RISK ACCOUNTS UNDER AUTONOMOUS MONITORING`);
        if (resolved > 0) dynamicItems.push(`${resolved} CASES RESOLVED // FRAUDGRAPH AGENT OPERATIVE`);

        // Pad with static items if needed
        const merged = dynamicItems.length >= 4
          ? dynamicItems
          : [...dynamicItems, ...FALLBACK_ITEMS.slice(dynamicItems.length)];

        setItems(merged);
      } catch {
        // Keep fallback
      }
    }
    void buildTicker();
  }, []);

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
