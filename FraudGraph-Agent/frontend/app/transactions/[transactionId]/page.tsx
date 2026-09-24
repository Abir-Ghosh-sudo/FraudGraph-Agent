"use client";

import React, { use } from "react";
import Link from "next/link";

export default function TransactionDetailPage({
  params,
}: {
  params: Promise<{ transactionId: string }>;
}) {
  const resolvedParams = use(params);

  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO CONSOLE
        </Link>
        <div className="brutal-card p-6 bg-white">
          <div className="tape-strip" />
          <span className="sticker sticker-yellow text-xs">TRANSACTION DETAILS</span>
          <h1 className="font-display text-4xl uppercase tracking-tight mt-2">
            LEDGER ENTRY: {resolvedParams.transactionId}
          </h1>
          <p className="font-mono text-sm text-[var(--muted)] mt-1">
            Real-time graph edge data · Settlement status · Risk factor attribution
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="bg-[var(--paper)] border-[3px] border-black p-4">
              <div className="font-mono text-xs font-bold text-[var(--muted)]">SETTLEMENT STATUS</div>
              <div className="font-display text-3xl text-[var(--red)]">FLAGGED / HELD</div>
            </div>
            <div className="bg-[var(--paper)] border-[3px] border-black p-4">
              <div className="font-mono text-xs font-bold text-[var(--muted)]">AMOUNT</div>
              <div className="font-display text-3xl text-black">$850,000</div>
            </div>
            <div className="bg-[var(--paper)] border-[3px] border-black p-4">
              <div className="font-mono text-xs font-bold text-[var(--muted)]">FRAUD SCORE</div>
              <div className="font-display text-3xl text-[var(--red)]">98/100</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
