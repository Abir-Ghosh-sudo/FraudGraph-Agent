"use client";

import React from "react";

interface HeroWord {
  text: string;
  tint?: "white" | "mint" | "sky" | "yellow" | "pink";
  rotation?: number;
}

export function HeroStack() {
  const words: HeroWord[] = [
    { text: "FRAUD", tint: "white", rotation: -1 },
    { text: "INVESTIGATION", tint: "mint", rotation: 0.5 },
    { text: "AGENT", tint: "sky", rotation: -0.7 },
  ];

  const tintClass = {
    white: "bg-white",
    mint: "bg-[var(--mint)]",
    sky: "bg-[var(--sky)]",
    yellow: "bg-[var(--yellow)]",
    pink: "bg-[var(--pink)]",
  };

  return (
    <div className="space-y-3 relative z-20">
      {words.map((w, idx) => (
        <div
          key={w.text}
          className={`hero-word ${tintClass[w.tint]} ${idx === 0 ? "tilt-left" : idx === 1 ? "" : "tilt-right"}`}
          style={{ transform: `rotate(${w.rotation}deg)` }}
        >
          {w.text}
        </div>
      ))}
    </div>
  );
}

export function HeroAnnotation() {
  return (
    <span className="font-handwritten text-xl sm:text-2xl text-[var(--pink)] -rotate-[2deg] inline-block ml-2 mt-2">
      NO BLIND DECISIONS
    </span>
  );
}

export function HeroSubtitle() {
  return (
    <p className="font-mono text-sm sm:text-base font-semibold leading-relaxed text-black max-w-2xl mt-6">
      AI-powered fraud investigation.
      <br />
      <span className="text-[var(--muted)]">
        From suspicious signal to defensible action.
      </span>
    </p>
  );
}

export function HeroCTAs() {
  return (
    <div className="flex flex-wrap items-center gap-4 mt-8">
      <a href="/investigations" className="btn-primary text-sm sm:text-base py-3 px-7">
        <span>START INVESTIGATION</span>
        <span className="text-lg">→</span>
      </a>
      <a href="/benchmark" className="btn-secondary text-sm sm:text-base py-3 px-7">
        <span>VIEW BENCHMARK</span>
      </a>
    </div>
  );
}

export function AnnotationTag({ text, color = "pink" }: { text: string; color?: "pink" | "mint" | "yellow" }) {
  const colorClass = {
    pink: "text-[var(--pink)]",
    mint: "text-[var(--mint-dark)]",
    yellow: "text-[var(--yellow-dark)]",
  };
  return (
    <span
      className={`font-handwritten text-lg sm:text-xl ${colorClass[color]} -rotate-[2deg] inline-block`}
    >
      {text}
    </span>
  );
}