"use client";

import React from "react";

interface BloopaHeroProps {
  onLaunchInvestigation: () => void;
  onViewDossier: () => void;
}

export function BloopaHero({
  onLaunchInvestigation,
  onViewDossier,
}: BloopaHeroProps) {
  return (
    <section className="relative w-full overflow-hidden pt-8 pb-14 px-4 sm:px-6">
      {/* -------------------------------------------------------------
          Collage Mixed-Media Background Layers (Matching Screenshots)
          ------------------------------------------------------------- */}
      <div className="absolute inset-0 pointer-events-none select-none z-0 overflow-hidden">
        {/* Left: Vintage Torn Newspaper Scrap */}
        <div
          className="absolute top-0 left-0 w-40 sm:w-64 h-full newspaper-clipping ripped-edge-right opacity-85 rotate-[-1deg]"
          aria-hidden="true"
        >
          <div className="p-3 text-[9px] sm:text-[10px] text-[#443e37] leading-[1.3] font-serif overflow-hidden h-full select-none">
            <div className="font-bold text-xs border-b border-[#333] pb-1 mb-1 uppercase tracking-wider">
              Financial Forensics Gazette
            </div>
            <p className="mb-2 italic">
              Autonomous multi-agent consensus dismantles multi-jurisdictional mule rings.
            </p>
            <p className="mb-2">
              TigerGraph deep graph traversals correlate rapid micro-structuring and layered smurfing patterns. Algorithmic reasoning generates court-admissible SAR evidence dossiers without manual latency...
            </p>
            <p className="hidden sm:block">
              Cognitive agents synthesize transaction graph embeddings with compliance policies to freeze compromised accounts in sub-second timeframes.
            </p>
          </div>
        </div>

        {/* Center: Torn Green Grass / Craft Paper Hill */}
        <div
          className="absolute top-4 sm:top-2 left-1/2 -translate-x-1/2 w-[340px] sm:w-[600px] md:w-[740px] h-[340px] sm:h-[400px] bg-[#68c948] ripped-edge-top-bottom opacity-90 shadow-md rotate-[1.5deg]"
          aria-hidden="true"
          style={{
            backgroundImage: `radial-gradient(#52a836 15%, transparent 16%), radial-gradient(#52a836 15%, transparent 16%)`,
            backgroundSize: `20px 20px`,
            backgroundPosition: `0 0, 10px 10px`,
          }}
        >
          <div className="w-full h-full bg-gradient-to-b from-[#7bdc5c]/40 to-[#4ca72e]/60" />
        </div>

        {/* Green Grass blades paper cutout illustration */}
        <div
          className="absolute top-6 right-16 sm:right-28 md:right-48 w-16 sm:w-24 h-16 sm:h-24 bg-[#42a826] rotate-[8deg] opacity-95"
          style={{
            clipPath: "polygon(20% 0%, 40% 100%, 60% 0%, 80% 100%, 100% 10%, 90% 100%, 0% 100%)",
          }}
          aria-hidden="true"
        />

        {/* Right: Notebook Math Grid Layer */}
        <div
          className="absolute top-0 right-0 w-36 sm:w-60 h-full notebook-grid ripped-edge-left opacity-90 rotate-[1deg]"
          aria-hidden="true"
        >
          {/* Masking tape on top right corner */}
          <div className="washi-tape absolute top-4 right-4 w-24 h-7 rotate-[-8deg] z-10" />
        </div>

        {/* Diagonal Washi Tape on top left */}
        <div className="washi-tape absolute top-6 left-16 sm:left-40 w-28 h-7 rotate-[12deg] z-10" />
      </div>

      {/* -------------------------------------------------------------
          Foreground Content
          ------------------------------------------------------------- */}
      <div className="relative z-10 max-w-[900px] mx-auto flex flex-col items-center text-center">
        {/* Top Tag Pill: ○ FOR AUTONOMOUS AGENTS */}
        <div className="mb-6 sm:mb-8 inline-flex items-center gap-2 bg-white border-[2.5px] border-black px-4 sm:px-5 py-1.5 shadow-[3px_3px_0_#050505] rotate-[-1deg] hover:rotate-0 transition-transform">
          <span className="w-2.5 h-2.5 rounded-full bg-[#ff6f91] border border-black inline-block animate-pulse" />
          <span className="font-mono text-xs sm:text-sm font-black uppercase tracking-wider text-black">
            FOR AUTONOMOUS AGENTS
          </span>
        </div>

        {/* Stacked Giant Brutalist Text Blocks matching Screenshot 5 */}
        <div className="flex flex-col items-center gap-3 sm:gap-4 my-2">
          {/* Row 1: FRAUD with handwritten cursive 'against' or 'for' */}
          <div className="relative inline-block rotate-[-1.5deg] hover:rotate-0 transition-transform">
            <div className="bg-white border-[3.5px] sm:border-[4.5px] border-black px-6 sm:px-12 py-2 sm:py-3.5 shadow-[7px_7px_0_#050505] sm:shadow-[10px_10px_0_#050505]">
              <h1 className="font-syne font-black text-5xl sm:text-7xl md:text-8xl tracking-tight text-black leading-none">
                FRAUD
              </h1>
            </div>
            {/* Handwritten script overlapping top right */}
            <span
              className="absolute -top-4 sm:-top-6 -right-6 sm:-right-8 font-caveat text-4xl sm:text-5xl text-[#ff6f91] font-bold rotate-[15deg] select-none pointer-events-none drop-shadow-[1px_1px_0_#000]"
              aria-hidden="true"
            >
              defense
            </span>
          </div>

          {/* Row 2: MACHINE */}
          <div className="inline-block rotate-[1deg] hover:rotate-0 transition-transform">
            <div className="bg-[#b9f5cf] border-[3.5px] sm:border-[4.5px] border-black px-6 sm:px-12 py-2 sm:py-3.5 shadow-[7px_7px_0_#050505] sm:shadow-[10px_10px_0_#050505]">
              <h2 className="font-syne font-black text-5xl sm:text-7xl md:text-8xl tracking-tight text-black leading-none">
                MACHINE
              </h2>
            </div>
          </div>

          {/* Row 3: INTELLIGENCE */}
          <div className="inline-block rotate-[-1deg] hover:rotate-0 transition-transform">
            <div className="bg-[#9cc9ff] border-[3.5px] sm:border-[4.5px] border-black px-6 sm:px-12 py-2 sm:py-3.5 shadow-[7px_7px_0_#050505] sm:shadow-[10px_10px_0_#050505]">
              <h2 className="font-syne font-black text-5xl sm:text-7xl md:text-8xl tracking-tight text-black leading-none">
                INTELLIGENCE
              </h2>
            </div>
          </div>
        </div>

        {/* Handwritten Green Subtitle */}
        <div className="mt-4 sm:mt-6 mb-8 sm:mb-10">
          <p className="font-caveat font-bold text-2xl sm:text-3xl md:text-4xl text-[#16a34a] -rotate-[1deg] tracking-wide">
            No blind decisions in the loop!
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6">
          {/* Coral Pink Launch Investigation Button */}
          <button
            type="button"
            onClick={onLaunchInvestigation}
            className="group relative bg-[#ff9aa2] hover:bg-[#ff858f] active:translate-x-[3px] active:translate-y-[3px] active:shadow-none border-[3.5px] border-black px-6 sm:px-10 py-3 sm:py-4 shadow-[6px_6px_0_#050505] hover:shadow-[3px_3px_0_#050505] transition-all cursor-pointer"
          >
            <span className="font-syne font-black text-base sm:text-lg uppercase tracking-wider text-black flex items-center gap-2">
              <span>START INVESTIGATION</span>
              <span className="text-xl group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </button>

          {/* White View Dossier Button */}
          <button
            type="button"
            onClick={onViewDossier}
            className="bg-white hover:bg-[#f8f8f8] active:translate-x-[3px] active:translate-y-[3px] active:shadow-none border-[3.5px] border-black px-6 sm:px-10 py-3 sm:py-4 shadow-[6px_6px_0_#050505] hover:shadow-[3px_3px_0_#050505] transition-all cursor-pointer"
          >
            <span className="font-syne font-black text-base sm:text-lg uppercase tracking-wider text-black">
              VIEW EVIDENCE DOSSIER
            </span>
          </button>
        </div>
      </div>
    </section>
  );
}
