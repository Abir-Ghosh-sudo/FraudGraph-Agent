"use client";

import React, { use } from "react";
import Link from "next/link";
import { CasePackCard } from "@/components/brutalist/CasePackCard";

export default function CaseDetailPage({ params }: { params: Promise<{ caseId: string }> }) {
  const resolvedParams = use(params);

  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/cases" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO ALL CASES
        </Link>
        <div className="flex items-center gap-3">
          <span className="sticker sticker-pink text-xs">CASE INSPECTION</span>
          <span className="font-mono text-sm font-bold">CASE ID: {resolvedParams.caseId}</span>
        </div>
        <CasePackCard onAction={(msg) => alert(msg)} onOpenModal={() => {}} />
      </div>
    </div>
  );
}
