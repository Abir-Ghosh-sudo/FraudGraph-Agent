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
    <section className="w-full max-w-full px-3 sm:px-6 pt-6 sm:pt-10 pb-12 sm:pb-16">
      {/* ---------------------------------------------------------------
          COLLAGE POSTER: torn paper frame wrapping an illustrated scene
      ---------------------------------------------------------------- */}
      <div className="relative mx-auto w-full max-w-[1180px] deckle-paper bg-[#fdf8f0] p-2.5 sm:p-4">
        <div className="relative w-full aspect-[4/5] sm:aspect-[1200/640] overflow-hidden bg-[#8fd0ef]">
          {/* ---------------- Illustrated paper-collage scene ------------- */}
          <svg
            className="absolute inset-0 w-full h-full"
            viewBox="0 0 1200 640"
            preserveAspectRatio="xMidYMid slice"
            aria-hidden="true"
            focusable="false"
          >
            <defs>
              <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2f9fd8" />
                <stop offset="55%" stopColor="#63c0ea" />
                <stop offset="100%" stopColor="#a8dcf2" />
              </linearGradient>

              <linearGradient id="hillGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#7cc94f" />
                <stop offset="100%" stopColor="#4f9c2c" />
              </linearGradient>

              <linearGradient id="hillFarGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8fd35f" />
                <stop offset="100%" stopColor="#63b23a" />
              </linearGradient>

              <radialGradient id="sunGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#ffe873" />
                <stop offset="100%" stopColor="#ffc933" />
              </radialGradient>

              <pattern
                id="grassBlades"
                width="26"
                height="26"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M13 26 L13 6 M13 12 L7 4 M13 16 L19 8"
                  stroke="#3d8520"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  fill="none"
                />
              </pattern>
            </defs>

            {/* Sky */}
            <rect x="0" y="0" width="1200" height="640" fill="url(#skyGrad)" />

            {/* Sun with hand-cut rays */}
            <g>
              {Array.from({ length: 12 }).map((_, i) => {
                const angle = (i * 30 * Math.PI) / 180;
                const inner = 66;
                const outer = 92;
                return (
                  <line
                    key={i}
                    x1={980 + inner * Math.cos(angle)}
                    y1={132 + inner * Math.sin(angle)}
                    x2={980 + outer * Math.cos(angle)}
                    y2={132 + outer * Math.sin(angle)}
                    stroke="#f5a623"
                    strokeWidth="7"
                    strokeLinecap="round"
                  />
                );
              })}
              <circle
                cx="980"
                cy="132"
                r="54"
                fill="url(#sunGrad)"
                stroke="#050505"
                strokeWidth="4"
              />
            </g>

            {/* Paper-cut clouds */}
            <g fill="#ffffff" stroke="#050505" strokeWidth="3.5">
              <g>
                <ellipse cx="215" cy="96" rx="78" ry="40" />
                <ellipse cx="165" cy="110" rx="48" ry="30" />
                <ellipse cx="272" cy="108" rx="52" ry="32" />
              </g>
              <g>
                <ellipse cx="700" cy="62" rx="62" ry="32" />
                <ellipse cx="658" cy="74" rx="40" ry="24" />
                <ellipse cx="746" cy="74" rx="42" ry="25" />
              </g>
              <g>
                <ellipse cx="1105" cy="205" rx="56" ry="28" />
                <ellipse cx="1068" cy="215" rx="36" ry="20" />
                <ellipse cx="1143" cy="215" rx="38" ry="21" />
              </g>
            </g>

            {/* Distant mountain range */}
            <g stroke="#050505" strokeWidth="3.5" strokeLinejoin="round">
              <path d="M690 340 L820 205 L950 340 Z" fill="#8fa8c8" />
              <path d="M880 345 L1010 178 L1160 345 Z" fill="#7387ad" />
              <path d="M600 348 L700 240 L800 348 Z" fill="#9db4d1" />
            </g>

            {/* Far rolling hill */}
            <path
              d="M0 402 Q300 342 620 392 T1200 372 L1200 640 L0 640 Z"
              fill="url(#hillFarGrad)"
              stroke="#050505"
              strokeWidth="3.5"
            />

            {/* Main grass hill */}
            <path
              d="M0 452 Q340 396 680 442 T1200 418 L1200 640 L0 640 Z"
              fill="url(#hillGrad)"
              stroke="#050505"
              strokeWidth="3.5"
            />

            {/* Grass blade texture clipped to the main hill */}
            <clipPath id="mainHillClip">
              <path d="M0 452 Q340 396 680 442 T1200 418 L1200 640 L0 640 Z" />
            </clipPath>
            <rect
              x="0"
              y="400"
              width="1200"
              height="240"
              fill="url(#grassBlades)"
              clipPath="url(#mainHillClip)"
              opacity="0.5"
            />

            {/* Left paper tree */}
            <g stroke="#050505" strokeWidth="3.5" strokeLinejoin="round">
              <rect x="176" y="300" width="20" height="130" fill="#8b5a2b" />
              <circle cx="186" cy="272" r="60" fill="#4a9e3a" />
              <circle cx="140" cy="306" r="44" fill="#57b043" />
              <circle cx="232" cy="304" r="46" fill="#3f8c31" />
            </g>

            {/* Right bushes */}
            <g stroke="#050505" strokeWidth="3.5">
              <path d="M1010 470 q0 -46 46 -46 q46 0 46 46 Z" fill="#4a9e3a" />
              <path d="M1100 480 q0 -38 38 -38 q38 0 38 38 Z" fill="#57b043" />
            </g>

            {/* Bottom-left flower cluster */}
            <g stroke="#050505" strokeWidth="2.5" strokeLinecap="round">
              {[
                { x: 120, y: 600, c: "#ff6f61" },
                { x: 186, y: 622, c: "#ffffff" },
                { x: 252, y: 604, c: "#ffe45c" },
                { x: 88, y: 632, c: "#ff9aa8" },
                { x: 316, y: 628, c: "#ff6f61" },
              ].map((f, i) => (
                <g key={i}>
                  <line
                    x1={f.x}
                    y1={f.y}
                    x2={f.x}
                    y2={f.y - 34}
                    stroke="#3d8520"
                    strokeWidth="4"
                  />
                  <g fill={f.c}>
                    <circle cx={f.x} cy={f.y - 46} r="9" />
                    <circle cx={f.x - 10} cy={f.y - 38} r="9" />
                    <circle cx={f.x + 10} cy={f.y - 38} r="9" />
                    <circle cx={f.x - 6} cy={f.y - 54} r="9" />
                    <circle cx={f.x + 6} cy={f.y - 54} r="9" />
                  </g>
                  <circle
                    cx={f.x}
                    cy={f.y - 46}
                    r="5"
                    fill="#ffd93b"
                    strokeWidth="2"
                  />
                </g>
              ))}
            </g>

            {/* Bottom-right duck */}
            <g stroke="#050505" strokeWidth="3.5" strokeLinejoin="round">
              <ellipse cx="1052" cy="556" rx="52" ry="34" fill="#e8a33d" />
              <circle cx="1096" cy="516" r="24" fill="#e8a33d" />
              <path d="M1116 512 L1146 520 L1116 528 Z" fill="#ff9d4d" />
              <circle cx="1102" cy="510" r="4" fill="#050505" stroke="none" />
              <path
                d="M1000 566 q26 22 52 0"
                fill="none"
                strokeWidth="3"
              />
            </g>
          </svg>

          {/* ------------- Torn newspaper strip on the left edge ---------- */}
          <div
            className="absolute left-0 top-0 h-full w-16 sm:w-28 torn-strip border-r-[3px] border-black/70 opacity-95 overflow-hidden select-none"
            aria-hidden="true"
          >
            <div className="p-2 text-[8px] sm:text-[10px] leading-[1.35] text-[#443e37]">
              <div className="font-bold text-[9px] sm:text-xs border-b border-[#333] pb-1 mb-1 uppercase tracking-wider">
                Financial Forensics Gazette
              </div>
              <p className="mb-1.5 italic">
                Multi-agent consensus dismantles multi-jurisdictional mule rings.
              </p>
              <p className="mb-1.5">
                TigerGraph deep traversal correlates rapid micro-structuring and
                layered smurfing patterns across the transaction graph.
              </p>
              <p className="hidden sm:block">
                Cognitive agents synthesize graph embeddings with compliance
                policy to freeze compromised accounts in sub-second timeframes.
              </p>
            </div>
          </div>

          {/* ------------------- Washi tape accents ---------------------- */}
          <div
            className="absolute top-2 left-24 sm:left-40 w-24 sm:w-32 h-6 sm:h-7 rotate-[-6deg] z-20"
            style={{ background: "rgba(255,228,92,0.92)" }}
            aria-hidden="true"
          />
          <div
            className="absolute top-3 right-24 sm:right-40 w-24 sm:w-32 h-6 sm:h-7 rotate-[5deg] z-20"
            style={{ background: "rgba(255,145,184,0.92)" }}
            aria-hidden="true"
          />
          <div
            className="absolute top-1/2 right-0 w-6 sm:w-7 h-24 sm:h-28 rotate-[2deg] z-20"
            style={{ background: "rgba(156,201,255,0.92)" }}
            aria-hidden="true"
          />
          <div
            className="absolute bottom-6 right-16 sm:right-32 w-24 sm:w-32 h-6 sm:h-7 rotate-[-4deg] z-20"
            style={{ background: "rgba(255,228,92,0.92)" }}
            aria-hidden="true"
          />

          {/* ------------------ Foreground title blocks ------------------ */}
          <div className="absolute inset-0 z-30 flex flex-col items-center justify-center px-3 sm:px-8">
            {/* Tag pill + overlapping script */}
            <div className="relative mb-2.5 sm:mb-4">
              <div className="inline-flex items-center gap-1.5 sm:gap-2 bg-white border-[2.5px] border-black px-2.5 sm:px-5 py-0.5 sm:py-1.5 shadow-[3px_3px_0_#050505] rotate-[-1deg] max-w-full">
                <span className="w-2 h-2 sm:w-2.5 sm:h-2.5 shrink-0 rounded-full bg-[#ff6f91] border border-black inline-block animate-pulse" />
                <span className="font-mono text-[9px] sm:text-sm font-black uppercase tracking-wider text-black whitespace-nowrap">
                  For Autonomous
                </span>
              </div>
              <span
                className="absolute -top-2.5 sm:-top-5 -right-4 sm:-right-10 font-caveat text-xl sm:text-4xl text-[#ff4f91] rotate-[12deg] select-none pointer-events-none drop-shadow-[1px_1px_0_#000]"
                aria-hidden="true"
              >
                defense!
              </span>
            </div>

            {/* Stacked title blocks */}
            <div className="flex flex-col items-center gap-2 sm:gap-3 w-full max-w-full">
              <div className="relative inline-block rotate-[-1.5deg] max-w-full">
                <div className="bg-white border-[3px] sm:border-[4px] border-black px-3 sm:px-7 py-0.5 sm:py-2 shadow-[4px_4px_0_#050505] sm:shadow-[7px_7px_0_#050505]">
                  <h1 className="font-syne font-black text-[clamp(1.6rem,5.2vw,3.75rem)] tracking-tight text-black leading-none">
                    FRAUD
                  </h1>
                </div>
              </div>

              <div className="inline-block rotate-[1deg] max-w-full">
                <div className="bg-[#b9f5cf] border-[3px] sm:border-[4px] border-black px-3 sm:px-7 py-0.5 sm:py-2 shadow-[4px_4px_0_#050505] sm:shadow-[7px_7px_0_#050505]">
                  <h2 className="font-syne font-black text-[clamp(1.6rem,5.2vw,3.75rem)] tracking-tight text-black leading-none">
                    MACHINE
                  </h2>
                </div>
              </div>

              <div className="inline-block rotate-[-1deg] max-w-full">
                <div className="bg-[#9cc9ff] border-[3px] sm:border-[4px] border-black px-2.5 sm:px-6 py-0.5 sm:py-2 shadow-[4px_4px_0_#050505] sm:shadow-[7px_7px_0_#050505]">
                  <h2 className="font-syne font-black text-[clamp(1.15rem,4.3vw,3.2rem)] tracking-tight text-black leading-none">
                    INTELLIGENCE
                  </h2>
                </div>
              </div>
            </div>

            {/* Script caption sitting on the grass */}
            <p className="mt-3 sm:mt-6 font-caveat font-bold text-base sm:text-2xl md:text-3xl text-[#1d4ed8] -rotate-[1deg] tracking-wide text-center px-2">
              No blind decisions in the loop!
            </p>
          </div>
        </div>
      </div>

      {/* ---------------------------------------------------------------
          Description card + CTAs (below the poster, per reference)
      ---------------------------------------------------------------- */}
      <div className="relative z-10 mx-auto w-full max-w-[1000px] -mt-2 sm:-mt-4 px-3 sm:px-6">
        <div className="bg-white border-[3px] sm:border-[4px] border-black p-5 sm:p-8 shadow-[7px_7px_0_#050505] text-center">
          <p className="font-mono text-[11px] sm:text-sm font-semibold text-neutral-800 leading-relaxed max-w-[62ch] mx-auto">
            Autonomous multi-agent consensus dismantles multi-jurisdictional mule
            rings. TigerGraph deep graph traversals correlate rapid smashing
            structuring and layering heuristics, while LangGraph cognitive agents
            reason over SAR evidence dossiers in sub-second execution windows.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3.5 sm:gap-6 mt-6 sm:mt-8">
            <button
              type="button"
              onClick={onLaunchInvestigation}
              className="group relative bg-[#ff9aa2] hover:bg-[#ff858f] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none border-[3px] sm:border-[3.5px] border-black px-4 sm:px-7 py-2.5 sm:py-3.5 shadow-[5px_5px_0_#050505] hover:shadow-[3px_3px_0_#050505] transition-all cursor-pointer"
            >
              <span className="font-syne font-black text-xs sm:text-base uppercase tracking-wider text-black flex items-center gap-2">
                <span>Start Investigation</span>
                <span className="text-lg group-hover:translate-x-1 transition-transform">
                  →
                </span>
              </span>
            </button>

            <button
              type="button"
              onClick={onViewDossier}
              className="bg-white hover:bg-[#f8f8f8] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none border-[3px] sm:border-[3.5px] border-black px-4 sm:px-7 py-2.5 sm:py-3.5 shadow-[5px_5px_0_#050505] hover:shadow-[3px_3px_0_#050505] transition-all cursor-pointer"
            >
              <span className="font-syne font-black text-xs sm:text-base uppercase tracking-wider text-black">
                View Evidence Dossier
              </span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
