"use client";

import React from "react";

export function ModelStatus() {
  return (
    <div className="brutal-card card-paper p-5 sm:p-6 relative">
      <div className="tape-strip" />
      <div className="flex items-center justify-between mb-4 border-b-[3px] border-black pb-2">
        <span className="sticker sticker-mint text-xs">MODEL INTEL</span>
        <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
          THE MODEL
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            ALGORITHM
          </div>
          <div className="font-display text-3xl mt-1">LightGBM</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            FEATURES
          </div>
          <div className="font-display text-3xl mt-1">147</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            STATUS
          </div>
          <div className="inline-flex items-center gap-2 mt-2 font-mono text-sm font-bold">
            <span className="w-3 h-3 rounded-full bg-[var(--mint)] border border-black status-dot-live" />
            ONLINE
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            TRAINED ON
          </div>
          <div className="font-display text-2xl mt-1">14,955</div>
          <div className="font-mono text-xs text-[var(--muted)]">labeled transactions</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            VALIDATION ROC-AUC
          </div>
          <div className="font-display text-3xl mt-1 text-[var(--mint-dark)]">0.9965</div>
        </div>
        <div className="bg-white border-[3px] border-black p-4 sm:col-span-2">
          <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)]">
            VALIDATION PR-AUC
          </div>
          <div className="font-display text-3xl mt-1 text-[var(--sky)]">0.9998</div>
        </div>
      </div>

      <div className="mt-4 bg-[var(--yellow)] border-[3px] border-black p-4 relative">
        <div className="font-mono text-xs font-black uppercase flex items-start gap-2">
          <span className="text-[var(--red)]">⚠</span>
          <span>
            Validation set is fraud-heavy. Metrics are not equivalent to benchmark accuracy.
            Do not quote these numbers as production performance.
          </span>
        </div>
      </div>
    </div>
  );
}