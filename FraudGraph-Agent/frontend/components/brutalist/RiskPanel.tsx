"use client";

import React from "react";

interface RiskBarProps {
  label: string;
  value: number; // 0-100
  tint?: "mint" | "sky" | "yellow" | "pink" | "red";
  maxLabel?: string;
}

export function RiskBar({ label, value, tint = "mint", maxLabel }: RiskBarProps) {
  const tintClass = {
    mint: "bg-[var(--mint)]",
    sky: "bg-[var(--sky)]",
    yellow: "bg-[var(--yellow)]",
    pink: "bg-[var(--pink)]",
    red: "bg-[var(--red)]",
  };
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between font-mono text-xs font-bold uppercase">
        <span>{label}</span>
        {maxLabel && <span className="text-[var(--muted)] normal-case">{maxLabel}</span>}
      </div>
      <div className="brutal-progress-outer">
        <div
          className={`brutal-progress-bar ${tintClass[tint]}`}
          style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

interface RiskPanelProps {
  score: number; // 0-100
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  bankModel?: number;
  mlModel?: number;
  graphEvidence?: number;
  historicalMatch?: number;
}

export function RiskPanel({
  score,
  level,
  bankModel = 0,
  mlModel = 0,
  graphEvidence = 0,
  historicalMatch = 0,
}: RiskPanelProps) {
  const levelTint = {
    LOW: "mint",
    MEDIUM: "yellow",
    HIGH: "pink",
    CRITICAL: "red",
  } as const;

  return (
    <div className="brutal-card card-paper p-5 sm:p-6 relative">
      <div className="tape-strip" />
      <div className="flex flex-col md:flex-row md:items-start gap-6">
        <div className="md:w-1/3">
          <div className="font-mono text-xs font-black uppercase text-[var(--muted)]">
            RISK SCORE
          </div>
          <div
            className={`font-display text-7xl sm:text-8xl leading-none mt-1 ${
              level === "CRITICAL"
                ? "text-[var(--red)]"
                : level === "HIGH"
                ? "text-[var(--pink)]"
                : level === "MEDIUM"
                ? "text-[var(--yellow)]"
                : "text-[var(--mint-dark)]"
            }`}
          >
            {score}
            <span className="text-3xl align-top">%</span>
          </div>
          <div
            className={`inline-block mt-2 font-mono text-xs font-black uppercase px-3 py-1 border-[2px] border-black ${
              level === "CRITICAL"
                ? "bg-[var(--red)] text-white"
                : level === "HIGH"
                ? "bg-[var(--pink)]"
                : level === "MEDIUM"
                ? "bg-[var(--yellow)]"
                : "bg-[var(--mint)]"
            }`}
          >
            {level} RISK
          </div>
        </div>
        <div className="md:w-2/3 space-y-4">
          <div className="font-mono text-xs font-black uppercase border-b-[2px] border-black pb-1">
            MODEL EVIDENCE BREAKDOWN
          </div>
          <RiskBar label="BANK MODEL" value={bankModel} tint="sky" />
          <RiskBar label="ML MODEL" value={mlModel} tint="mint" />
          <RiskBar label="GRAPH EVIDENCE" value={graphEvidence} tint="yellow" />
          <RiskBar label="HISTORICAL MATCH" value={historicalMatch} tint="pink" />
        </div>
      </div>
    </div>
  );
}