"use client";

import React, { useState } from "react";
import { BloopaHeader } from "@/components/bloopa/BloopaHeader";
import { BloopaHero } from "@/components/bloopa/BloopaHero";
import { BloopaTicker } from "@/components/bloopa/BloopaTicker";
import { BloopaStats } from "@/components/bloopa/BloopaStats";
import { BloopaFeatures } from "@/components/bloopa/BloopaFeatures";
import { BloopaProtocolSection } from "@/components/bloopa/BloopaProtocolSection";
import { BloopaBottomBar } from "@/components/bloopa/BloopaBottomBar";
import { RealCaseDossierModal } from "@/components/bloopa/RealCaseDossierModal";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";
import { ContractModal } from "@/components/bloopa/ContractModal";
import { DocsModal } from "@/components/bloopa/DocsModal";
import { WalletModal } from "@/components/bloopa/WalletModal";
import { useDashboardStats } from "@/hooks/use-dashboard";
import Link from "next/link";

export default function Home() {
  const { stats } = useDashboardStats(15000);

  // Modals state
  const [dossierModalOpen, setDossierModalOpen] = useState(false);
  const [protocolModalOpen, setProtocolModalOpen] = useState(false);
  const [contractModalOpen, setContractModalOpen] = useState(false);
  const [docsModalOpen, setDocsModalOpen] = useState(false);
  const [walletModalOpen, setWalletModalOpen] = useState(false);

  // Simulated Agent Wallet connection
  const [walletConnected, setWalletConnected] = useState(true);
  const [walletAddress, setWalletAddress] = useState<string | null>("AGENT-ALGO-0x89F3A9");

  // Selected Tier in Protocol Modal
  const [selectedTier, setSelectedTier] = useState<string>("Fresh");
  const [selectedCap, setSelectedCap] = useState<number>(0.1);

  // Toast notifications
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3800);
  };

  const handleSelectTier = (tier: string, cap: number) => {
    setSelectedTier(tier);
    setSelectedCap(cap);
    setProtocolModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#f7f4ea] text-black flex flex-col font-sans selection:bg-[#ffe45c] selection:text-black">
      {/* 1. Header (Top Announcement Bar + Main Nav Box) */}
      <BloopaHeader
        onOpenDossier={() => setDocsModalOpen(true)}
        onOpenConsole={() => setProtocolModalOpen(true)}
        activeCasesCount={stats.activeCases}
      />

      {/* 2. Hero Section (Paper Collage + Stacked Typography) */}
      <main className="flex-1">
        <BloopaHero
          onLaunchInvestigation={() => setProtocolModalOpen(true)}
          onViewDossier={() => setDossierModalOpen(true)}
        />

        {/* 3. Black Ticker Tape: Retro daisy flower symbols with real fraud alerts */}
        <BloopaTicker theme="black" />

        {/* 4. Stats Section: Numbers don't lie... (Connected to real backend stats) */}
        <BloopaStats />

        {/* 5. Yellow Ticker Tape */}
        <BloopaTicker theme="yellow" />

        {/* 6. Seed your Growth Feature Section (Exact 3x2 brutalist cards) */}
        <BloopaFeatures />

        {/* 7. How It Works (Vertical Stepper 01-03) & Tier-Based Credit Caps (V2) / The Math */}
        <BloopaProtocolSection
          onSelectTier={handleSelectTier}
          onLaunchProtocol={() => setProtocolModalOpen(true)}
        />

        {/* Direct Access Bar to Full Investigations & Graph Engine */}
        <section className="max-w-[1240px] mx-auto px-4 sm:px-6 pb-12 pt-4">
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[6px_6px_0_#050505] flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="sticker sticker-mint text-xs font-mono font-bold">
                TIGERGRAPH AI
              </span>
              <div>
                <h4 className="font-syne font-black text-lg text-black uppercase">
                  FraudGraph Autonomous Intelligence Suite
                </h4>
                <p className="font-mono text-xs text-neutral-600 font-semibold">
                  Multi-agent consensus, real-time evidence dossiers, and live transaction graph reasoning.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/investigations"
                className="bg-[#ffe45c] hover:bg-[#fed932] border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs uppercase shadow-[3px_3px_0_#050505] transition-transform active:translate-x-[1px] active:translate-y-[1px]"
              >
                INVESTIGATIONS ({stats.activeCases || 4}) →
              </Link>
              <Link
                href="/graph"
                className="bg-white hover:bg-neutral-100 border-[2.5px] border-black px-4 py-2 font-mono font-black text-xs uppercase shadow-[3px_3px_0_#050505] transition-transform active:translate-x-[1px] active:translate-y-[1px]"
              >
                GRAPH VIEW →
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* 8. Bottom Sticky Status Bar */}
      <BloopaBottomBar
        walletConnected={walletConnected}
        onOpenContract={() => setContractModalOpen(true)}
      />

      {/* Interactive Modals */}
      <RealCaseDossierModal
        isOpen={dossierModalOpen}
        onClose={() => setDossierModalOpen(false)}
        onShowToast={showToast}
      />

      <ProtocolModal
        isOpen={protocolModalOpen}
        onClose={() => setProtocolModalOpen(false)}
        walletConnected={walletConnected}
        onOpenWallet={() => setWalletModalOpen(true)}
        selectedTier={selectedTier}
        selectedCap={selectedCap}
        onSuccessToast={showToast}
      />

      <ContractModal
        isOpen={contractModalOpen}
        onClose={() => setContractModalOpen(false)}
      />

      <DocsModal
        isOpen={docsModalOpen}
        onClose={() => setDocsModalOpen(false)}
      />

      <WalletModal
        isOpen={walletModalOpen}
        onClose={() => setWalletModalOpen(false)}
        walletConnected={walletConnected}
        walletAddress={walletAddress}
        algoBalance={24.85}
        onConnect={(addr) => {
          setWalletConnected(true);
          setWalletAddress(addr);
          showToast(`⚡ Connected agent wallet: ${addr}`);
        }}
        onDisconnect={() => {
          setWalletConnected(false);
          setWalletAddress(null);
          showToast("🔌 Wallet disconnected.");
        }}
      />

      {/* Interactive Toast Notification */}
      {toastMessage && (
        <div
          role="alert"
          aria-live="polite"
          className="fixed bottom-14 right-4 sm:right-6 z-50 bg-[#b9f5cf] border-[3px] border-black shadow-[6px_6px_0_#050505] px-5 py-3 font-mono text-xs sm:text-sm font-black text-black animate-[slide-in-toast_0.2s_ease-out] flex items-center gap-3 select-none"
        >
          <span>{toastMessage}</span>
          <button
            type="button"
            onClick={() => setToastMessage(null)}
            className="text-xs font-bold font-mono hover:text-red-700 ml-2"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}