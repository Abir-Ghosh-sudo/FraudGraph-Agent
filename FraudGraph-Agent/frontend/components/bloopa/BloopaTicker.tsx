"use client";

import React, { useEffect, useState } from "react";
import { casesApi } from "@/lib/api";
import type { Case } from "@/types/case";

interface BloopaTickerProps {
  theme?: "black" | "yellow";
  defaultText?: string;
}

export function BloopaTicker({
  theme = "black",
  defaultText,
}: BloopaTickerProps) {
  const isBlack = theme === "black";

  // Exact required phrases from Section 21
  const baseItems = isBlack
    ? [
        "AUTONOMOUS FRAUD INVESTIGATION",
        "TIGERGRAPH GRAPH CONSENSUS",
        "EVIDENCE-FIRST DECISIONS",
        "MULTI-AGENT INVESTIGATION",
        "NEXT-BEST ACTION",
      ]
    : [
        "PROTECT YOUR CAPITAL",
        "REAL-TIME TRANSACTION MONITORING",
        "INSTANT SAR DOSSIER GENERATION",
        "EVIDENCE-FIRST POLICY GATES",
        "HIGH-FREQUENCY ACCOUNT DEFENSE",
      ];

  const [items, setItems] = useState<string[]>(
    defaultText ? [defaultText] : baseItems
  );

  useEffect(() => {
    async function loadRealTicker() {
      try {
        const raw = await casesApi.list<unknown>();
        const cases = Array.isArray(raw) ? (raw as Case[]) : [];
        if (cases.length > 0 && isBlack) {
          const dynamic = cases.slice(0, 3).map((c) => {
            const risk = c.risk_score ? `${Math.round(c.risk_score * 100)}% RISK` : "FLAGGED";
            return `CASE ${c.case_id.slice(0, 8).toUpperCase()} // ${c.title.toUpperCase()} [${risk}]`;
          });
          setItems([...dynamic, ...baseItems]);
        }
      } catch {
        // use default baseItems
      }
    }
    void loadRealTicker();
  }, [isBlack]);

  const displayList = [...items, ...items, ...items];

  return (
    <div
      className={`w-full max-w-full overflow-hidden border-y-[3.5px] border-black select-none ${
        isBlack ? "bg-black text-white" : "bg-[#ffe45c] text-black"
      }`}
    >
      <div className="flex whitespace-nowrap py-2 sm:py-2.5 font-syne font-black text-sm sm:text-base uppercase tracking-wider animate-[marquee_28s_linear_infinite] hover:[animation-play-state:paused] motion-reduce:animate-none">
        {displayList.map((item, idx) => (
          <div key={idx} className="inline-flex items-center gap-3 sm:gap-5 mx-3 sm:mx-4 shrink-0">
            <span
              className={`text-base sm:text-lg font-normal leading-none ${
                isBlack ? "text-white" : "text-black"
              }`}
              aria-hidden="true"
            >
              ✿
            </span>
            <span className="truncate max-w-[260px] sm:max-w-none">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
