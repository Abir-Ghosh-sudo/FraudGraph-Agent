"use client";

import React from "react";
import { useDashboardStats } from "@/hooks/use-dashboard";

export function BloopaStats() {
  const { stats, loading, error } = useDashboardStats(10000);

  // Every figure below comes from the backend. Nothing is invented: when the
  // API has no data we render an em dash rather than a plausible-looking
  // placeholder.
  const displayStats = [
    {
      value: loading ? "—" : String(stats.activeCases),
      unit: stats.activeCases === 1 ? "case" : "cases",
      handwritten: "Active Pipeline",
      tilt: "rotate-[-1deg]",
    },
    {
      value: loading ? "—" : String(stats.highRiskCases),
      unit: stats.highRiskCases === 1 ? "threat" : "threats",
      handwritten: "High Risk Alerts",
      tilt: "rotate-[1deg]",
    },
    {
      // The benchmark answer key is withheld, so accuracy is not computable.
      value: loading
        ? "—"
        : stats.accuracyAvailable && stats.meanRiskScore !== null
          ? `${stats.meanRiskScore}%`
          : "N/A",
      unit: "",
      handwritten: "Model Accuracy",
      tilt: "rotate-[-0.5deg]",
    },
    {
      // Mean risk score from real case data (0-100).
      value: loading ? "—" : stats.meanRiskScore !== null ? String(stats.meanRiskScore) : "—",
      unit: "avg risk",
      handwritten: "Mean Risk Score",
      tilt: "rotate-[1deg]",
    },
  ];

  return (
    <section className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 py-10 sm:py-12">
      {/* Tilted Sticker: Numbers don't lie... */}
      <div className="mb-5 sm:mb-6 flex items-center justify-between gap-4 flex-wrap">
        <div className="inline-block bg-white border-[3px] border-black px-4 sm:px-5 py-1.5 shadow-[4px_4px_0_#050505] rotate-[-2deg]">
          <span className="font-caveat font-bold text-2xl sm:text-3xl text-black">
            Numbers don&apos;t lie...
          </span>
        </div>

        <span className="font-mono text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.18em] text-neutral-600">
          {error
            ? "BACKEND UNREACHABLE"
            : `LIVE // ${stats.totalCases} CASES INDEXED`}
        </span>
      </div>

      {error ? (
        <div className="mb-5 border-[3px] border-black bg-[#ff9aa2] px-4 py-2.5 shadow-[4px_4px_0_#050505]">
          <p className="font-mono text-[11px] sm:text-xs font-bold uppercase text-black">
            Live metrics unavailable — cannot reach the FraudGraph API. Start
            the backend on port 8000 to populate these figures.
          </p>
        </div>
      ) : null}

      {/* 4 Brutalist Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
        {displayStats.map((item, idx) => (
          <div
            key={idx}
            className={`bg-white border-[3.5px] border-black p-4 sm:p-5 shadow-[5px_5px_0_#050505] hover:shadow-[7px_7px_0_#050505] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all ${item.tilt} hover:rotate-0 flex flex-col justify-between min-w-0`}
          >
            {/* Top row: Big number + unit */}
            <div className="flex items-baseline gap-1.5 sm:gap-2 mb-3 min-w-0">
              <span className="font-syne font-black text-3xl sm:text-4xl lg:text-5xl text-black leading-none tracking-tight truncate">
                {item.value}
              </span>
              {item.unit && (
                <span className="font-mono text-[10px] sm:text-xs lg:text-sm font-bold uppercase text-[#737373] whitespace-nowrap">
                  {item.unit}
                </span>
              )}
            </div>

            {/* Bottom row: Handwritten green badge label */}
            <div className="pt-2 border-t-2 border-dashed border-neutral-200">
              <span className="font-caveat font-bold text-lg sm:text-2xl lg:text-3xl text-[#22c55e] block leading-tight">
                {item.handwritten}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
