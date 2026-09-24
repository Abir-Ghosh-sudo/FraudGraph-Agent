"use client";

import React, { use } from "react";
import Link from "next/link";
import { AgentCognitionStream } from "@/components/brutalist/AgentCognitionStream";

export default function InvestigationDetailPage({
  params,
}: {
  params: Promise<{ caseId: string }>;
}) {
  const resolvedParams = use(params);

  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/investigations" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO INVESTIGATIONS
        </Link>
        <div className="flex items-center gap-3">
          <span className="sticker sticker-yellow text-xs">INVESTIGATION PIPELINE</span>
          <span className="font-mono text-sm font-bold">CASE ID: {resolvedParams.caseId}</span>
        </div>
        <AgentCognitionStream onAction={(msg) => alert(msg)} />
      </div>
    </div>
  );
}
