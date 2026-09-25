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

  const fallbackItems = isBlack
    ? [
        "AUTONOMOUS FRAUD INVESTIGATION",
        "TIGERGRAPH GRAPH CONSENSUS",
        "ZERO FALSE POSITIVES",
        "MULTI-AGENT SYNDICATE DETECTION",
        "78.4ms GRAPH TRAVERSAL LATENCY",
      ]
    : [
        "PROTECT YOUR CAPITAL",
        "REAL-TIME TRANSACTION MONITORING",
        "INSTANT SAR DOSSIER GENERATION",
        "EVIDENCE-FIRST POLICY GATES",
        "HIGH-FREQUENCY ACCOUNT DEFENSE",
      ];

  const [items, setItems] = useState<string[]>(
    defaultText ? [defaultText] : fallbackItems
  );

  useEffect(() => {
    async function loadRealTicker() {
      try {
        const raw = await casesApi.list<unknown>();
        const cases = Array.isArray(raw) ? (raw as Case[]) : [];
        if (cases.length > 0 && isBlack) {
          const dynamic = cases.slice(0, 4).map((c) => {
            const risk = c.risk_score ? `${Math.round(c.risk_score * 100)}% RISK` : "FLAGGED";
            return `CASE ${c.case_id.slice(0, 8).toUpperCase()} // ${c.title.toUpperCase()} [${risk}]`;
          });
          setItems([...dynamic, ...fallbackItems.slice(0, 2)]);
        }
      } catch {
        // use fallbacks
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
      <div className="flex whitespace-nowrap py-2 sm:py-2.5 font-syne font-black text-base sm:text-lg uppercase tracking-wider animate-[marquee_25s_linear_infinite]">
        {displayList.map((item, idx) => (
          <div key={idx} className="inline-flex items-center gap-4 sm:gap-6 mx-3 sm:mx-4">
            <span
              className={`text-lg sm:text-xl font-normal leading-none ${
                isBlack ? "text-white" : "text-black"
              }`}
              aria-hidden="true"
            >
              ✿
            </span>
            <span className="truncate max-w-[280px] sm:max-w-none">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
