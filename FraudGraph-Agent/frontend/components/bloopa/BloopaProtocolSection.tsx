"use client";

import React, { useState } from "react";

interface BloopaProtocolSectionProps {
  onSelectTier?: (tier: string, cap: number) => void;
  onLaunchProtocol?: () => void;
}

export function BloopaProtocolSection({
  onSelectTier,
  onLaunchProtocol,
}: BloopaProtocolSectionProps) {
  const [activeTab, setActiveTab] = useState<"how-it-works" | "the-math">("how-it-works");

  // Math simulation interactive states
  const [simCentrality, setSimCentrality] = useState<number>(65);
  const [simVelocity, setSimVelocity] = useState<number>(80);
  const [simTrust, setSimTrust] = useState<number>(15);

  // Dynamic formula calculation
  // Risk = min(100, Math.round((simCentrality * 0.45 + simVelocity * 0.45) * (1 - simTrust / 150)))
  const calculatedRisk = Math.min(
    100,
    Math.max(5, Math.round((simCentrality * 0.5 + simVelocity * 0.5) * (1 - simTrust / 150)))
  );

  return (
    <section id="protocol-section" className="w-full max-w-[1240px] mx-auto px-4 sm:px-6 py-14">
      {/* -------------------------------------------------------------
          Brutalist Tab Switchers: [ How It Works ] & [ The Math ]
          ------------------------------------------------------------- */}
      <div className="flex flex-wrap items-center gap-3 sm:gap-6 mb-10 select-none">
        {/* Tab 1: How It Works */}
        <button
          type="button"
          onClick={() => setActiveTab("how-it-works")}
          className={`px-4 sm:px-8 py-2 sm:py-3.5 border-[3.5px] border-black transition-all cursor-pointer font-syne font-black text-lg sm:text-3xl uppercase tracking-tight ${
            activeTab === "how-it-works"
              ? "bg-white shadow-[6px_6px_0_#050505] rotate-[-1.5deg]"
              : "bg-[#f7f4ea] hover:bg-white text-neutral-600 shadow-[3px_3px_0_#050505] rotate-0"
          }`}
        >
          How It Works
        </button>

        {/* Tab 2: The Math */}
        <button
          type="button"
          onClick={() => setActiveTab("the-math")}
          className={`px-4 sm:px-8 py-2 sm:py-3.5 border-[3.5px] border-black transition-all cursor-pointer font-syne font-black text-lg sm:text-3xl uppercase tracking-tight ${
            activeTab === "the-math"
              ? "bg-white shadow-[6px_6px_0_#050505] rotate-[1.5deg]"
              : "bg-[#f7f4ea] hover:bg-white text-neutral-600 shadow-[3px_3px_0_#050505] rotate-0"
          }`}
        >
          The Math
        </button>
      </div>

      {/* -------------------------------------------------------------
          TAB CONTENT 1: How It Works (Exact match to Screenshot 1)
          ------------------------------------------------------------- */}
      {activeTab === "how-it-works" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          {/* LEFT COLUMN: Vertical Stepper Pipeline (Steps 01, 02, 03) */}
          <div className="lg:col-span-6 relative pl-6 sm:pl-10">
            {/* Continuous Vertical Rail Line */}
            <div
              className="absolute left-[38px] sm:left-[54px] top-6 bottom-10 w-[3px] bg-neutral-300"
              aria-hidden="true"
            />

            <div className="space-y-8 sm:space-y-10">
              {/* STEP 01 */}
              <div className="relative">
                {/* Header Row: Box 01 + Header Box */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white border-[3px] border-black flex items-center justify-center font-mono font-black text-sm sm:text-base text-black shadow-[3px_3px_0_#050505] z-10">
                    01
                  </div>
                  <div className="bg-white border-[3px] border-black px-4 py-1.5 shadow-[3px_3px_0_#050505]">
                    <h3 className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                      Ingest & Link
                    </h3>
                  </div>
                </div>

                {/* Content Box */}
                <div className="ml-12 sm:ml-14 bg-white border-[3px] border-black p-4 sm:p-5 shadow-[4px_4px_0_#050505]">
                  <p className="font-mono text-xs sm:text-sm font-semibold text-neutral-800 leading-relaxed">
                    Stream transaction telemetry into TigerGraph. Construct dynamic account & mule relationship graphs.
                  </p>
                </div>
              </div>

              {/* STEP 02 */}
              <div className="relative">
                {/* Header Row: Box 02 (Mint) + Header Box */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-[#b9f5cf] border-[3px] border-black flex items-center justify-center font-mono font-black text-sm sm:text-base text-black shadow-[3px_3px_0_#050505] z-10">
                    02
                  </div>
                  <div className="bg-white border-[3px] border-black px-4 py-1.5 shadow-[3px_3px_0_#050505]">
                    <h3 className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                      Reason & Prove
                    </h3>
                  </div>
                </div>

                {/* Content Box */}
                <div className="ml-12 sm:ml-14 bg-white border-[3px] border-black p-4 sm:p-5 shadow-[4px_4px_0_#050505]">
                  <p className="font-mono text-xs sm:text-sm font-semibold text-neutral-800 leading-relaxed">
                    LangGraph cognitive agents query hybrid graph retrieval, testing policy violations and mule patterns.
                  </p>
                </div>
              </div>

              {/* STEP 03 */}
              <div className="relative">
                {/* Header Row: Box 03 + Header Box */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white border-[3px] border-black flex items-center justify-center font-mono font-black text-sm sm:text-base text-black shadow-[3px_3px_0_#050505] z-10">
                    03
                  </div>
                  <div className="bg-white border-[3px] border-black px-4 py-1.5 shadow-[3px_3px_0_#050505]">
                    <h3 className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                      Defensible Action
                    </h3>
                  </div>
                </div>

                {/* Content Box */}
                <div className="ml-12 sm:ml-14 bg-white border-[3px] border-black p-4 sm:p-5 shadow-[4px_4px_0_#050505]">
                  <p className="font-mono text-xs sm:text-sm font-semibold text-neutral-800 leading-relaxed">
                    Synthesize FinCEN SAR dockets, trigger automated transaction freezes, and escalate high-risk cases.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Tier-Based Enforcement Caps Card */}
          <div className="lg:col-span-6">
            <div className="bg-white border-[3.5px] sm:border-[4px] border-black p-6 sm:p-8 shadow-[8px_8px_0_#050505]">
              {/* Card Title + Policy ID */}
              <div className="flex items-start justify-between gap-4 mb-4">
                <h3 className="font-caveat font-bold text-2xl sm:text-3xl text-black leading-tight">
                  Risk-Based Enforcement Tiers (V2)
                </h3>
                <span className="font-mono text-[10px] font-black uppercase tracking-[0.14em] text-neutral-600 whitespace-nowrap pt-1.5">
                  POLICY ID: RE-V908
                </span>
              </div>

              {/* Solid Black Separator Line */}
              <div className="w-full h-[3px] bg-black mb-6" />

              {/* Tier Rows */}
              <div className="space-y-5">
                {/* Tier 1: Fresh */}
                <div className="flex items-center justify-between gap-3 pb-5 border-b-2 border-dashed border-neutral-300">
                  <span className="font-mono text-sm sm:text-base font-bold text-neutral-900">
                    Fresh / Verified (0-30)
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      onSelectTier?.("Fresh", 0.1);
                      onLaunchProtocol?.();
                    }}
                    className="bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs sm:text-sm text-black shadow-[3px_3px_0_#050505] cursor-pointer transition-transform"
                  >
                    0.05% Watch / draw
                  </button>
                </div>

                {/* Tier 2: Trusted */}
                <div className="flex items-center justify-between gap-3 pb-5 border-b-2 border-dashed border-neutral-300">
                  <span className="font-mono text-sm sm:text-base font-bold text-neutral-900">
                    Suspicious Activity (30-70)
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      onSelectTier?.("Trusted", 0.5);
                      onLaunchProtocol?.();
                    }}
                    className="bg-[#b9f5cf] hover:bg-[#a1f1bc] active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs sm:text-sm text-black shadow-[3px_3px_0_#050505] cursor-pointer transition-transform"
                  >
                    Step-Up Auth / draw
                  </button>
                </div>

                {/* Tier 3: Veteran */}
                <div className="flex items-center justify-between gap-3 pb-5 border-b-2 border-dashed border-neutral-300">
                  <span className="font-mono text-sm sm:text-base font-bold text-neutral-900">
                    High Risk Syndicate (70-90)
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      onSelectTier?.("Veteran", 2.0);
                      onLaunchProtocol?.();
                    }}
                    className="bg-[#9cc9ff] hover:bg-[#85beff] active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs sm:text-sm text-black shadow-[3px_3px_0_#050505] cursor-pointer transition-transform"
                  >
                    Auto-Freeze 24h
                  </button>
                </div>

                {/* Tier 4: Elite */}
                <div className="flex items-center justify-between gap-3">
                  <span className="font-mono text-sm sm:text-base font-bold text-neutral-900">
                    Confirmed Fraud (90+)
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      onSelectTier?.("Elite", 5.0);
                      onLaunchProtocol?.();
                    }}
                    className="bg-[#ffe45c] hover:bg-[#fcd935] active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs sm:text-sm text-black shadow-[3px_3px_0_#050505] cursor-pointer transition-transform"
                  >
                    Instant SAR Docket
                  </button>
                </div>
              </div>

              {/* Consensus Rule */}
              <div className="mt-6 border-[2.5px] border-dashed border-neutral-400 p-3.5 bg-[#f7f4ea]">
                <p className="font-mono text-[11px] sm:text-xs font-semibold text-neutral-800 leading-relaxed">
                  <span className="font-black text-black">Consensus Rule:</span>{" "}
                  3-of-4 cognitive LangGraph nodes must sign off with TigerGraph
                  graph votes ≥ 0.8 prior to triggering autonomous enforcement.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* -------------------------------------------------------------
          TAB CONTENT 2: The Math (Fraud Scoring Engine)
          ------------------------------------------------------------- */}
      {activeTab === "the-math" && (
        <div className="bg-white border-[3.5px] sm:border-[4px] border-black p-6 sm:p-10 shadow-[8px_8px_0_#050505]">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left: Formula explanation */}
            <div className="lg:col-span-7 space-y-5">
              <span className="sticker sticker-mint text-xs font-mono font-bold">
                TIGERGRAPH HYBRID SCORING MODEL
              </span>
              <h3 className="font-syne font-black text-2xl sm:text-4xl uppercase text-black">
                Graph Consensus & Risk Formula
              </h3>
              <p className="font-mono text-xs sm:text-sm font-semibold text-neutral-700 leading-relaxed">
                Risk is evaluated across TigerGraph graph centrality metrics and transaction velocity vectors. No unexplainable black-box scores.
              </p>

              {/* Math Code Box */}
              <div className="bg-[#f7f4ea] border-[2.5px] border-black p-4 font-mono text-xs sm:text-sm shadow-[3px_3px_0_#050505] space-y-2">
                <div className="text-neutral-500 font-bold">// Graph Consensus Formula</div>
                <div className="text-black font-black text-sm sm:text-base">
                  RiskScore = min(100, (Centrality × 0.50 + Velocity × 0.50) × (1 - Trust / 150))
                </div>
                <div className="text-neutral-600 text-xs">
                  • 3-Hop mule path analysis • sub-80ms execution • FinCEN-admissible evidence trail
                </div>
              </div>

              {/* Interactive Sliders */}
              <div className="space-y-4 pt-3">
                {/* Slider 1: Centrality */}
                <div>
                  <div className="flex justify-between font-mono text-xs font-bold mb-1">
                    <span>Graph Centrality / Cycle Risk:</span>
                    <span className="font-black text-black">{simCentrality}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={simCentrality}
                    onChange={(e) => setSimCentrality(Number(e.target.value))}
                    className="w-full accent-black cursor-pointer"
                  />
                </div>

                {/* Slider 2: Velocity */}
                <div>
                  <div className="flex justify-between font-mono text-xs font-bold mb-1">
                    <span>Transaction Velocity Anomaly:</span>
                    <span className="font-black text-black">{simVelocity}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={simVelocity}
                    onChange={(e) => setSimVelocity(Number(e.target.value))}
                    className="w-full accent-black cursor-pointer"
                  />
                </div>

                {/* Slider 3: Trust Factor */}
                <div>
                  <div className="flex justify-between font-mono text-xs font-bold mb-1">
                    <span>Historical Account Trust:</span>
                    <span className="font-black text-[#16a34a]">{simTrust}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={simTrust}
                    onChange={(e) => setSimTrust(Number(e.target.value))}
                    className="w-full accent-black cursor-pointer"
                  />
                </div>
              </div>
            </div>

            {/* Right: Real-time Calculated Result Box */}
            <div className="lg:col-span-5 bg-[#ffe45c] border-[3.5px] border-black p-6 sm:p-8 shadow-[6px_6px_0_#050505] text-center flex flex-col justify-between">
              <div>
                <span className="font-mono text-xs font-black uppercase tracking-wider text-black block mb-2">
                  COMPUTED RISK SCORE
                </span>
                <div className="font-syne font-black text-6xl sm:text-7xl text-black leading-none my-4">
                  {calculatedRisk}%
                </div>
                <span className="font-mono text-sm font-bold text-neutral-800">
                  {calculatedRisk >= 75 ? "CRITICAL THREAT" : calculatedRisk >= 40 ? "SUSPICIOUS" : "LOW RISK"}
                </span>
              </div>

              <div className="mt-6 pt-4 border-t-2 border-black/20 text-left space-y-1 font-mono text-xs font-semibold text-neutral-900">
                <div className="flex justify-between">
                  <span>Enforcement:</span>
                  <span className="font-black">
                    {calculatedRisk >= 75
                      ? "Immediate Account Freeze"
                      : calculatedRisk >= 40
                      ? "Step-Up Authentication"
                      : "Allow Transaction"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Audit Trail:</span>
                  <span className="font-black">100% Provenance Saved</span>
                </div>
              </div>

              <button
                type="button"
                onClick={onLaunchProtocol}
                className="mt-6 w-full bg-white hover:bg-neutral-100 active:translate-x-[2px] active:translate-y-[2px] border-[3px] border-black py-3 font-syne font-black uppercase text-sm tracking-wider shadow-[3px_3px_0_#050505] cursor-pointer transition-all"
              >
                OPEN INVESTIGATION CONSOLE →
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
