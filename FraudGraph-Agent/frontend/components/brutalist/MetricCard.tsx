"use client";

import React from "react";

interface MetricCardProps {
  value: string;
  label: string;
  sublabel?: string;
  tint?: "mint" | "sky" | "yellow" | "pink" | "red" | "green" | "white" | "lavender";
  rotation?: number;
  className?: string;
}

const tintClass = {
  mint: "card-mint",
  sky: "card-sky",
  yellow: "card-yellow",
  pink: "card-pink",
  red: "bg-[var(--red)] text-white",
  green: "bg-[var(--green)] text-black",
  white: "card-paper",
  lavender: "bg-[var(--lavender)]",
};

export function MetricCard({
  value,
  label,
  sublabel,
  tint = "white",
  rotation = 0,
  className = "",
}: MetricCardProps) {
  return (
    <div
      className={`brutal-card ${tintClass[tint]} relative ${className}`}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <div className="font-mono text-xs sm:text-sm font-black uppercase tracking-wider">
        {label}
      </div>
      <div className="font-display text-4xl sm:text-5xl mt-1 leading-none">
        {value}
      </div>
      {sublabel && (
        <div className="font-mono text-[11px] sm:text-xs font-bold text-black/70 mt-2">
          {sublabel}
        </div>
      )}
    </div>
  );
}

interface InvestigationBoardProps {
  children: React.ReactNode;
  heading?: string;
  subheading?: string;
  sticker?: string;
}

export function InvestigationBoard({
  children,
  heading = "THE INVESTIGATION BOARD",
  subheading,
  sticker = "CONTROL ROOM",
}: InvestigationBoardProps) {
  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b-[3px] border-black pb-3">
        <div className="flex items-center gap-3">
          <span className="sticker sticker-yellow text-xs">{sticker}</span>
          <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl uppercase tracking-tight">
            {heading}
          </h2>
        </div>
        {subheading && (
          <span className="font-mono text-xs font-bold text-[var(--muted)]">
            {subheading}
          </span>
        )}
      </div>
      {children}
    </section>
  );
}