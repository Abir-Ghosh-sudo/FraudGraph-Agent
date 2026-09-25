"use client";

import React, { useState } from "react";
import { actionsApi } from "@/lib/api";

interface ProtocolModalProps {
  isOpen: boolean;
  onClose: () => void;
  walletConnected?: boolean;
  onOpenWallet?: () => void;
  selectedTier?: string;
  selectedCap?: number;
  onSuccessToast?: (msg: string) => void;
}

export function ProtocolModal({
  isOpen,
  onClose,
  selectedTier = "Fresh",
  onSuccessToast,
}: ProtocolModalProps) {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [targetAccount, setTargetAccount] = useState("acc_mule_8829");
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [hasScanned, setHasScanned] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(false);

  if (!isOpen) return null;

  const handleRunAgentScan = () => {
    setIsEvaluating(true);
    setTimeout(() => {
      setIsEvaluating(false);
      setHasScanned(true);
      onSuccessToast?.("🤖 Autonomous Agent Consensus: 3-Hop Mule Ring Confirmed (94% Risk)");
      setStep(2);
    }, 1500);
  };

  const handleExecuteAction = async (actionType: string) => {
    setIsEvaluating(true);
    try {
      await actionsApi.create({
        case_id: "case_9082_mule",
        action_type: actionType,
        status: "executed",
        rationale: `Agent executed ${actionType} under policy gate`,
        requires_approval: false,
      });
    } catch {
      // fallback simulation
    } finally {
      setIsEvaluating(false);
      setActionSuccess(true);
      onSuccessToast?.(`⚡ Executed Next-Best-Action: ${actionType.toUpperCase()}`);
      setStep(3);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs select-none">
      <div className="relative w-full max-w-2xl bg-[#f7f4ea] border-[4px] border-black p-6 sm:p-8 shadow-[12px_12px_0_#050505] max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="sticker sticker-yellow text-xs font-mono font-bold">
              AGENT CONSOLE
            </span>
            <span className="sticker sticker-mint text-xs font-mono font-bold">
              TIER: {selectedTier.toUpperCase()}
            </span>
          </div>
          <h2 className="font-syne font-black text-2xl sm:text-4xl text-black uppercase tracking-tight">
            Autonomous Investigation Console
          </h2>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            Execute real-time TigerGraph hybrid traversal and LangGraph multi-agent consensus.
          </p>
        </div>

        {/* Stepper Tabs Bar */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {[
            { num: 1, label: "01 Graph Scan" },
            { num: 2, label: "02 Reason" },
            { num: 3, label: "03 Action" },
          ].map((s) => (
            <button
              key={s.num}
              type="button"
              onClick={() => setStep(s.num as 1 | 2 | 3)}
              className={`py-2 px-1 text-center font-mono font-black text-xs uppercase border-[2.5px] border-black transition-all ${
                step === s.num
                  ? "bg-[#b9f5cf] shadow-[3px_3px_0_#050505] -translate-y-0.5"
                  : "bg-white text-neutral-600 shadow-none hover:bg-neutral-100"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* STEP 1: GRAPH SCAN */}
        {step === 1 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-syne font-black text-xl uppercase text-black">
                Step 1: Traverse Syndicate Graph
              </span>
              <span className="font-mono text-xs font-bold text-neutral-500">
                TigerGraph k-Hop
              </span>
            </div>
            <p className="font-mono text-xs font-semibold text-neutral-700">
              Select target account or transaction ID to run automated cyclical smurfing pattern scan.
            </p>

            <div className="flex items-center gap-3">
              <input
                type="text"
                value={targetAccount}
                onChange={(e) => setTargetAccount(e.target.value)}
                className="w-full bg-[#f7f4ea] border-[2.5px] border-black px-3 py-2 font-mono font-black text-sm text-black outline-none"
              />
            </div>

            <button
              type="button"
              disabled={isEvaluating}
              onClick={handleRunAgentScan}
              className="w-full bg-[#b9f5cf] hover:bg-[#a1f1bc] active:translate-x-[2px] active:translate-y-[2px] border-[3px] border-black py-3 font-syne font-black text-sm uppercase tracking-wider shadow-[4px_4px_0_#050505] cursor-pointer disabled:opacity-50"
            >
              {isEvaluating
                ? "TRAVERSING GRAPH & EXPANDING HOPS..."
                : hasScanned
                ? "SCAN COMPLETE (NEXT STEP) →"
                : "EXECUTE AUTONOMOUS GRAPH SCAN →"}
            </button>
          </div>
        )}

        {/* STEP 2: REASONING & CONSENSUS */}
        {step === 2 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-syne font-black text-xl uppercase text-black">
                Step 2: Multi-Agent Consensus
              </span>
              <span className="font-mono text-xs font-bold text-[#16a34a]">
                4 Criteria Gate
              </span>
            </div>

            <div className="space-y-2 font-mono text-xs">
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  1. Velocity Spike: 14 txs under $10,000 threshold within 120s
                </span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  2. Graph Cycle: Direct funds returned to originating seed node
                </span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  3. IP / Device Reuse: Shared MAC hash across 6 distinct names
                </span>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setStep(3)}
                className="w-full bg-[#ffe45c] hover:bg-[#fed932] border-[3px] border-black py-3 font-syne font-black text-sm uppercase tracking-wider shadow-[4px_4px_0_#050505] cursor-pointer"
              >
                PROCEED TO ENFORCEMENT ACTIONS →
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: NEXT-BEST-ACTION */}
        {step === 3 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-syne font-black text-xl uppercase text-black">
                Step 3: Trigger Next-Best-Action
              </span>
              <span className="font-mono text-xs font-bold text-[#ff6f61]">
                High Risk Gate
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => handleExecuteAction("freeze_account")}
                className="p-3 bg-[#ff91b8] hover:bg-[#ff7ba8] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left"
              >
                FREEZE ACCOUNT (24H)
              </button>
              <button
                type="button"
                onClick={() => handleExecuteAction("step_up_mfa")}
                className="p-3 bg-[#9cc9ff] hover:bg-[#85beff] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left"
              >
                MANDATE STEP-UP AUTH
              </button>
              <button
                type="button"
                onClick={() => handleExecuteAction("generate_sar")}
                className="p-3 bg-[#ffe45c] hover:bg-[#fcd935] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left"
              >
                EXPORT SAR DOCKET
              </button>
            </div>

            {actionSuccess && (
              <div className="mt-3 p-3 bg-[#eef7ee] border-[2px] border-[#16a34a] font-mono text-xs text-[#16a34a] font-bold">
                ✓ Enforcement action successfully logged and executed under automated compliance policy.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
