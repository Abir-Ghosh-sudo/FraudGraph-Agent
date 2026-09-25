"use client";

import React from "react";

export function BloopaFeatures() {
  const features = [
    {
      icon: "◇",
      iconBg: "bg-[#b9f5cf]", // mint
      title: "Stake & Lock",
      description:
        "Your stake is your trust signal — lock collateral to unlock high-frequency agent transaction limits.",
    },
    {
      icon: "↑",
      iconBg: "bg-[#9cc9ff]", // sky
      title: "Build History",
      description:
        "Record payments on-chain and in graph memory. Each verified interaction boosts your algorithmic score.",
    },
    {
      icon: "◈",
      iconBg: "bg-[#ffe45c]", // yellow
      title: "Draw Credit",
      description:
        "Borrow liquidity after the LLM oracle approves your task. Caps rise from 0.1 → 5 ALGO as you level up.",
    },
    {
      icon: "↺",
      iconBg: "bg-[#ff91b8]", // pink
      title: "Repay & Grow",
      description:
        "Settle debt to dynamically increase credit limits. Prove reliability, gain defense capital.",
    },
    {
      icon: "⚡",
      iconBg: "bg-[#b9f5cf]", // mint
      title: "Instant Auth",
      description:
        "Operations settle in seconds. TigerGraph & Algorand speed enables high-frequency agent actions.",
    },
    {
      icon: "✕",
      iconBg: "bg-[#9cc9ff]", // sky
      title: "Trust Protocol",
      description:
        "Bad actors get slashed. Defaulters and mule rings lose their stake instantly to the treasury.",
    },
  ];

  return (
    <section className="w-full max-w-[1240px] mx-auto px-4 sm:px-6 py-14">
      {/* Centered Heading Banner */}
      <div className="flex flex-col items-center text-center mb-12 sm:mb-16">
        <div className="inline-block bg-white border-[3.5px] sm:border-[4px] border-black px-6 sm:px-12 py-3 sm:py-4 shadow-[7px_7px_0_#050505] rotate-[-1deg] hover:rotate-0 transition-transform">
          <h2 className="font-syne font-black text-3xl sm:text-5xl md:text-6xl text-black tracking-tight uppercase">
            Seed your Growth
          </h2>
        </div>

        {/* Subtitle */}
        <p className="font-caveat font-bold text-2xl sm:text-3xl text-neutral-800 mt-4 tracking-wide">
          Features designed for agents moving at machine speed!
        </p>
      </div>

      {/* 6 Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        {features.map((feat, idx) => (
          <div
            key={idx}
            className="group bg-white border-[3.5px] border-black p-6 sm:p-7 shadow-[6px_6px_0_#050505] hover:shadow-[10px_10px_0_#050505] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all flex flex-col justify-start relative"
          >
            {/* Square Icon Badge */}
            <div
              className={`w-12 h-12 ${feat.iconBg} border-[2.5px] border-black flex items-center justify-center text-xl sm:text-2xl font-black text-black shadow-[3px_3px_0_#050505] mb-5 select-none`}
            >
              {feat.icon}
            </div>

            {/* Feature Title */}
            <h3 className="font-syne font-black text-2xl sm:text-3xl text-black tracking-tight uppercase mb-3">
              {feat.title}
            </h3>

            {/* Feature Description */}
            <p className="font-mono text-xs sm:text-sm font-semibold text-neutral-800 leading-relaxed">
              {feat.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
