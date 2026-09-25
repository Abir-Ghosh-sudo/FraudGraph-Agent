"use client";

import React from "react";

interface TimelineStep {
  number: string;
  title: string;
  description: string;
  tint?: "mint" | "sky" | "yellow" | "pink" | "red";
}

const tintClass = {
  mint: "bg-[var(--mint)]",
  sky: "bg-[var(--sky)]",
  yellow: "bg-[var(--yellow)]",
  pink: "bg-[var(--pink)]",
  red: "bg-[var(--red)]",
};

export function InvestigationTimeline({ steps }: { steps: TimelineStep[] }) {
  return (
    <div className="brutal-card card-paper p-5 sm:p-6 relative">
      <div className="tape-strip" />
      <div className="flex items-center justify-between mb-4 border-b-[3px] border-black pb-2">
        <span className="sticker sticker-sky text-xs">INVESTIGATION FLOW</span>
        <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
          TIMELINE
        </h2>
      </div>
      <div className="space-y-0">
        {steps.map((step, idx) => (
          <React.Fragment key={step.number}>
            <div className="flex items-start gap-4 py-3">
              <div className="flex flex-col items-center">
                <div
                  className={`w-12 h-12 flex items-center justify-center font-display text-xl border-[3px] border-black ${tintClass[step.tint || "mint"]}`}
                >
                  {step.number}
                </div>
                {idx < steps.length - 1 && (
                  <div className="w-1 h-8 bg-black my-1" />
                )}
              </div>
              <div className="flex-1 pt-1">
                <div className="font-display text-lg sm:text-xl uppercase tracking-tight">
                  {step.title}
                </div>
                <div className="font-mono text-xs sm:text-sm font-semibold text-black/80 mt-1">
                  {step.description}
                </div>
              </div>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export function DefaultTimeline() {
  const steps: TimelineStep[] = [
    { number: "01", title: "TRIGGER", description: "Fraud signal received", tint: "pink" },
    { number: "02", title: "INVESTIGATE", description: "Transaction loaded", tint: "sky" },
    { number: "03", title: "EVIDENCE", description: "Device relationship discovered", tint: "sky" },
    { number: "04", title: "PATTERN", description: "Card-not-present detected", tint: "yellow" },
    { number: "05", title: "RISK", description: "0.91 HIGH", tint: "red" },
    { number: "06", title: "ACTION", description: "Step-up authentication", tint: "mint" },
  ];
  return <InvestigationTimeline steps={steps} />;
}