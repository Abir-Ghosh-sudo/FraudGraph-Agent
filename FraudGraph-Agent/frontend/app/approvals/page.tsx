"use client";

import React, { useState } from "react";
import Link from "next/link";
import { InvestigationBoard } from "@/components/brutalist/MetricCard";
import { ApprovalDocument } from "@/components/brutalist/NBAAndApproval";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { Navbar } from "@/components/brutalist/Navbar";

export default function ApprovalsPage() {
  const [toast, setToast] = useState<string | null>(null);
  const showToast = (msg: string) => setToast(msg);

  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar activeTab="approvals" onShowToast={showToast} />
      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-8">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <InvestigationBoard heading="HUMAN APPROVAL QUEUE" sticker="APPROVALS">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ApprovalDocument
              action="BLOCK CARD"
              risk="CRITICAL"
              exposure="$2,840"
              policy="L2 APPROVAL REQUIRED"
              onApprove={() => showToast("Approved action.")}
              onReject={() => showToast("Rejected action.")}
              onMoreEvidence={() => showToast("Requested more evidence.")}
            />
            <ApprovalDocument
              action="FREEZE ACCOUNT"
              risk="HIGH"
              exposure="$14,200"
              policy="L1 APPROVAL REQUIRED"
              onApprove={() => showToast("Approved action.")}
              onReject={() => showToast("Rejected action.")}
              onMoreEvidence={() => showToast("Requested more evidence.")}
            />
          </div>
        </InvestigationBoard>
      </main>
      <BottomStatus />
    </div>
  );
}