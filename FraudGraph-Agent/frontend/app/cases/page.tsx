"use client";

import React from "react";
import Link from "next/link";
import { CasePackCard } from "@/components/brutalist/CasePackCard";

export default function CasesPage() {
  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          ← BACK TO FRAUDGRAPH CONSOLE
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <span className="sticker sticker-yellow text-xs">DOSSIER REGISTRY</span>
            <h1 className="font-display text-4xl uppercase tracking-tight mt-1">
              ACTIVE FRAUD CASES & SYNDICATES
            </h1>
          </div>
          <span className="status">
            <span className="status-dot-alert" />
            <span>03 ACTIVE DOSSIERS</span>
          </span>
        </div>
        <CasePackCard onAction={(msg) => alert(msg)} onOpenModal={() => {}} />
      </div>
    </div>
  );
}
