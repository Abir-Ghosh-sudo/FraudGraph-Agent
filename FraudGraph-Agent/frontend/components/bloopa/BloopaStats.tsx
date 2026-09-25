"use client";

import React from "react";
import { useDashboardStats } from "@/hooks/use-dashboard";

export function BloopaStats() {
  const { stats, loading } = useDashboardStats(10000);

  const displayStats = [
    {
      value: loading ? "—" : String(stats.activeCases || 4),
      unit: "cases",
      handwritten: "Active Pipeline",
      tilt: "rotate-[-1deg]",
    },
    {
      value: loading ? "—" : String(stats.highRiskCases || 1),
      unit: "threats",
      handwritten: "High Risk Alerts",
      tilt: "rotate-[1deg]",
    },
    {
      value: loading ? "—" : String(stats.modelConfidence || 98),
      unit: "%",
      handwritten: "Model Accuracy",
      tilt: "rotate-[-0.5deg]",
    },
    {
      value: "24",
      unit: "hrs",
      handwritten: "Repay Window",
      tilt: "rotate-[1deg]",
    },
  ];

  return (
    <section className="w-full max-w-[1240px] mx-auto px-4 sm:px-6 py-12">
      {/* Tilted Sticker: Numbers don't lie... */}
      <div className="mb-6">
        <div className="inline-block bg-white border-[3px] border-black px-4 sm:px-5 py-1.5 shadow-[4px_4px_0_#050505] rotate-[-2deg]">
          <span className="font-caveat font-bold text-2xl sm:text-3xl text-black">
            Numbers don&apos;t lie...
          </span>
        </div>
      </div>

      {/* 4 Brutalist Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6">
        {displayStats.map((item, idx) => (
          <div
            key={idx}
            className={`bg-white border-[3.5px] border-black p-6 sm:p-7 shadow-[6px_6px_0_#050505] hover:shadow-[8px_8px_0_#050505] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all ${item.tilt} hover:rotate-0 flex flex-col justify-between`}
          >
            {/* Top row: Big number + muted unit */}
            <div className="flex items-baseline gap-2 mb-3">
              <span className="font-syne font-black text-5xl sm:text-6xl text-black leading-none tracking-tight">
                {item.value}
              </span>
              <span className="font-mono font-bold text-lg sm:text-xl text-[#737373]">
                {item.unit}
              </span>
            </div>

            {/* Bottom row: Handwritten green badge label */}
            <div className="pt-2 border-t-2 border-dashed border-neutral-200">
              <span className="font-caveat font-bold text-2xl sm:text-3xl text-[#22c55e] block">
                {item.handwritten}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
