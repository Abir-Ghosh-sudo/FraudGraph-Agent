"use client";

import React from "react";

export function BloopaFeatures() {
  const features = [
    {
      icon: "◇",
      iconBg: "bg-[#b9f5cf]", // mint
      title: "Stake & Lock",
      description:
        "Your stake is your trust signal — lock collateral to unlock high-frequency agent transaction limits and autonomous dispute clearing.",
      meta: "MIN. COLLATERAL: 100 ALGO",
      status: "STAKED OK",
      statusColor: "text-[#16a34a]",
    },
    {
      icon: "↑",
      iconBg: "bg-[#9cc9ff]", // sky
      title: "Build History",
      description:
        "Record payments on-chain and in graph memory. Each verified interaction boosts your algorithmic risk score.",
      meta: "GRAPH DEPTH: 8 HOPS",
      status: "INDEXED",
      statusColor: "text-[#1d4ed8]",
    },
    {
      icon: "◈",
      iconBg: "bg-[#ffe45c]", // yellow
      title: "Draw Credit",
      description:
        "Borrow liquidity after the LLM oracle approves your task. Caps rise from 0.1 → 5 ALGO as you level up.",
      meta: "TIER: LVL 2 VERIFIED",
      status: "CAP: 2.5 ALGO",
      statusColor: "text-[#b45309]",
    },
    {
      icon: "↺",
      iconBg: "bg-[#ff91b8]", // pink
      title: "Repay & Grow",
      description:
        "Settle debt to dynamically increase credit limits. Prove reliability, gain multi-syndicate defense capital.",
      meta: "WINDOW: 24 HOURS",
      status: "AUTO-SETTLE",
      statusColor: "text-[#be185d]",
    },
    {
      icon: "⚡",
      iconBg: "bg-[#b9f5cf]", // mint
      title: "Instant Auth",
      description:
        "Operations settle in seconds. TigerGraph & Algorand speed enables high-frequency agent actions without risking manual intervention.",
      meta: "LATENCY: 85ms AVG",
      status: "SUB-SECOND",
      statusColor: "text-[#16a34a]",
    },
    {
      icon: "✕",
      iconBg: "bg-[#9cc9ff]", // sky
      title: "Trust Protocol",
      description:
        "Bad actors get slashed. Defaulters, and correlated mule rings lose their stake instantly to the community collateral depository insurance treasury.",
      meta: "SLASH RATIO: 100%",
      status: "ZERO TOLERANCE",
      statusColor: "text-[#dc2626]",
    },
  ];

  return (
    <section className="w-full max-w-[1240px] mx-auto px-4 sm:px-6 py-14">
      {/* Centered Heading Banner */}
      <div className="flex flex-col items-center text-center mb-10 sm:mb-14">
        <div className="inline-block max-w-full bg-white border-[3.5px] sm:border-[4px] border-black px-4 sm:px-9 py-2 sm:py-3.5 shadow-[7px_7px_0_#050505] rotate-[-1deg] hover:rotate-0 transition-transform">
          <h2 className="font-syne font-black text-[clamp(1.5rem,5vw,3.5rem)] text-black tracking-tight uppercase">
            Seed your Growth
          </h2>
        </div>

        {/* Subtitle */}
        <p className="font-caveat font-bold text-lg sm:text-2xl lg:text-3xl text-neutral-800 mt-3 tracking-wide px-2 max-w-full">
          Features designed for agents moving at machine speed!
        </p>
      </div>

      {/* 6 Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        {features.map((feat, idx) => (
          <div
            key={idx}
            className="group bg-white border-[3.5px] border-black p-5 sm:p-7 shadow-[6px_6px_0_#050505] hover:shadow-[10px_10px_0_#050505] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all flex flex-col justify-start relative min-w-0"
          >
            {/* Square Icon Badge */}
            <div
              className={`w-12 h-12 ${feat.iconBg} border-[2.5px] border-black flex items-center justify-center text-xl sm:text-2xl font-black text-black shadow-[3px_3px_0_#050505] mb-5 select-none`}
            >
              {feat.icon}
            </div>

            {/* Feature Title */}
            <h3 className="font-syne font-black text-xl sm:text-2xl lg:text-3xl text-black tracking-tight uppercase mb-3 break-words">
              {feat.title}
            </h3>

            {/* Feature Description */}
            <p className="font-mono text-[11px] sm:text-[13px] font-semibold text-neutral-800 leading-relaxed flex-1">
              {feat.description}
            </p>

            {/* Bottom meta row: left mono detail + right colored status */}
            <div className="mt-5 pt-3 border-t-2 border-dashed border-neutral-300 flex items-center justify-between gap-2 sm:gap-3 min-w-0">
              <span className="font-mono text-[10px] sm:text-[11px] font-bold uppercase tracking-wide text-neutral-600 truncate">
                {feat.meta}
              </span>
              <span
                className={`font-mono text-[10px] sm:text-[11px] font-black uppercase tracking-wide whitespace-nowrap ${feat.statusColor}`}
              >
                {feat.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
