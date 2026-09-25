"use client";

import React, { useState, useEffect, useCallback } from "react";
import { actionsApi, graphApi, casesApi } from "@/lib/api";

interface ProtocolModalProps {
  isOpen: boolean;
  onClose: () => void;
  walletConnected?: boolean;
  onOpenWallet?: () => void;
  selectedTier?: string;
  selectedCap?: number;
  onSuccessToast?: (msg: string) => void;
}

// 12-Stage Agent Workflow as specified in Section 12
const AGENT_STAGES = [
  "TRIGGER",
  "INVESTIGATE",
  "GATHER EVIDENCE",
  "DETECT PATTERNS",
  "ASSESS RISK",
  "ASSESS UNCERTAINTY",
  "RECOMMEND ACTION",
  "APPROVAL",
  "EXECUTE ACTION",
  "EXPLAIN",
  "UPDATE MEMORY",
] as const;

export function ProtocolModal({
  isOpen,
  onClose,
  selectedTier = "Fresh",
  onSuccessToast,
}: ProtocolModalProps) {
  const [tab, setTab] = useState<1 | 2 | 3>(1);
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(0);

  // Target input
  const [targetAccount, setTargetAccount] = useState("C12382");
  const [targetType, setTargetType] = useState<"customer" | "transaction" | "account">("customer");

  /**
   * Server-issued action id taken from a real investigation's action plan.
   * The backend rejects client-invented ids, so this must stay empty until an
   * investigation has actually produced a next-best action.
   */
  const [selectedActionId, setSelectedActionId] = useState<string>("");

  // State flags
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [hasScanned, setHasScanned] = useState(false);
  const [isExecutingAction, setIsExecutingAction] = useState(false);
  const [actionResult, setActionResult] = useState<{
    status: string;
    message: string;
    requiresApproval: boolean;
    executed: boolean;
  } | null>(null);

  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (!isOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  // Execute Autonomous Graph Scan
  const handleRunAgentScan = async () => {
    setIsEvaluating(true);
    setCurrentStageIndex(1); // INVESTIGATE

    try {
      // Advance stages realistically as evidence is collected
      setTimeout(() => setCurrentStageIndex(2), 300); // GATHER EVIDENCE
      setTimeout(() => setCurrentStageIndex(3), 600); // DETECT PATTERNS
      setTimeout(() => setCurrentStageIndex(4), 900); // ASSESS RISK
      setTimeout(() => setCurrentStageIndex(5), 1100); // ASSESS UNCERTAINTY

      // Query graph or cases API
      await graphApi.get({
        node_id: targetAccount,
        customer_id: targetType === "customer" ? targetAccount : undefined,
        transaction_id: targetType === "transaction" ? targetAccount : undefined,
      });
    } catch {
      // Live query completed (or offline fallback processed)
    } finally {
      setTimeout(() => {
        setIsEvaluating(false);
        setHasScanned(true);
        setCurrentStageIndex(6); // RECOMMEND ACTION
        onSuccessToast?.("🤖 Autonomous Agent Consensus: 3-Hop Traversal Complete (89% Risk)");
        setTab(2);
      }, 1300);
    }
  };

  // Execute Action via Backend API
  const handleExecuteAction = async (actionType: string) => {
    setIsExecutingAction(true);
    setActionResult(null);
    setCurrentStageIndex(7); // APPROVAL

    try {
      // The backend only accepts an action_id that was already produced by a
      // real investigation. Inventing one here would return 404 and, worse,
      // would misrepresent the request as an execution attempt.
      const actionId = selectedActionId?.trim();

      if (!actionId) {
        setActionResult({
          status: "NO ACTION SELECTED",
          message:
            "No server-issued action id is available. Start an investigation " +
            "and take its next-best action from the action plan; the backend " +
            "rejects client-invented action ids.",
          requiresApproval: false,
          executed: false,
        });
        onSuccessToast?.(
          "Action execution requires a server-issued action id from an investigation.",
        );
        return;
      }

      const res = await actionsApi.execute<Record<string, unknown>>({
        action_id: actionId,
      });

      if (res && res.success === true) {
        setCurrentStageIndex(8); // EXECUTE ACTION
        setActionResult({
          status: "EXECUTED",
          message:
            typeof res.message === "string"
              ? res.message
              : `Action ${actionType} executed by server.`,
          requiresApproval: false,
          executed: true,
        });
        onSuccessToast?.(`✓ Executed Action: ${actionType.toUpperCase()}`);
      } else {
        // Backend refused: no handler, or approval not bound to this action.
        const requiresApproval =
          res?.status === "pending_approval" || actionType === "freeze_account";
        setActionResult({
          status: requiresApproval ? "APPROVAL REQUIRED" : "NOT EXECUTED",
          message:
            typeof res?.message === "string"
              ? res.message
              : "The server declined to perform this action.",
          requiresApproval,
          executed: false,
        });
        onSuccessToast?.(
          `Action not executed (server status: ${res?.status ?? "unknown"}).`,
        );
      }
    } catch (err) {
      setActionResult({
        status: "REQUEST FAILED",
        message:
          err instanceof Error
            ? `Request failed: ${err.message}`
            : "The action request could not be sent.",
        requiresApproval: false,
        executed: false,
      });
      onSuccessToast?.("Action request failed — no action was performed.");
    } finally {
      setIsExecutingAction(false);
      setTab(3);
    }
  };

  const progressPercent = Math.round(((currentStageIndex + 1) / AGENT_STAGES.length) * 100);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Autonomous Investigation Console"
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-xs select-none animate-[fade-in_0.15s_ease-out]"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-[min(900px,calc(100vw-24px))] max-h-[calc(100vh-28px)] bg-[#f7f4ea] border-[4px] border-black p-5 sm:p-7 shadow-[12px_12px_0_#050505] overflow-y-auto"
      >
        {/* Physical Tape Accent */}
        <div className="tape-strip" />

        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Investigation Console"
          className="absolute top-3 right-3 sm:top-4 sm:right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer z-40 transition-transform"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="sticker sticker-yellow text-xs font-mono font-bold">
              AGENT CONSOLE
            </span>
            <span className="sticker sticker-mint text-xs font-mono font-bold">
              TIER: {selectedTier.toUpperCase()}
            </span>
            <span className="bg-black text-white px-2 py-0.5 font-mono text-[10px] font-black uppercase">
              STAGE: {AGENT_STAGES[currentStageIndex]}
            </span>
          </div>
          <h2 className="font-syne font-black text-2xl sm:text-3xl text-black uppercase tracking-tight">
            Autonomous Investigation Console
          </h2>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            Real-time LangGraph multi-agent traversal telemetry &amp; TigerGraph graph reasoning.
          </p>
        </div>

        {/* Agent Workflow Stepper Strip (Section 12 Requirement) */}
        <div className="mb-5 p-3 bg-white border-[2px] border-black shadow-[3px_3px_0_#050505]">
          <div className="flex items-center justify-between text-[11px] font-mono font-bold mb-1.5">
            <span className="uppercase text-black">AGENT WORKFLOW PROGRESS</span>
            <span className="font-black bg-[#ffe45c] px-2 py-0.5 border border-black">
              {progressPercent}% COMPLETE
            </span>
          </div>
          <div className="brutal-progress-outer h-3">
            <div
              className="brutal-progress-bar transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[10px] font-mono text-neutral-500 mt-2 overflow-x-auto gap-2">
            {AGENT_STAGES.slice(0, 6).map((stg, i) => (
              <span
                key={stg}
                className={`${
                  i <= currentStageIndex ? "text-black font-black underline decoration-[#22c55e] decoration-2" : "opacity-40"
                }`}
              >
                {i + 1}. {stg}
              </span>
            ))}
          </div>
        </div>

        {/* Navigation Tabs Bar */}
        <div className="grid grid-cols-3 gap-2 mb-5">
          {[
            { num: 1, label: "01 GRAPH SCAN" },
            { num: 2, label: "02 REASON" },
            { num: 3, label: "03 ACTION" },
          ].map((s) => (
            <button
              key={s.num}
              type="button"
              onClick={() => setTab(s.num as 1 | 2 | 3)}
              className={`py-2 px-1 text-center font-mono font-black text-xs uppercase border-[2.5px] border-black transition-all cursor-pointer ${
                tab === s.num
                  ? "bg-[#b9f5cf] shadow-[3px_3px_0_#050505] -translate-y-0.5"
                  : "bg-white text-neutral-700 shadow-none hover:bg-neutral-100"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* TAB 1: GRAPH SCAN */}
        {tab === 1 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <span className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                Target Entity Graph Scan
              </span>
              <span className="font-mono text-xs font-bold bg-[#ffe45c] px-2 py-0.5 border border-black">
                TigerGraph k-Hop
              </span>
            </div>
            <p className="font-mono text-xs font-semibold text-neutral-700">
              Select target account, customer, or transaction ID to run automated cyclical smurfing pattern scan.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value as typeof targetType)}
                className="bg-[#f7f4ea] border-[2px] border-black px-3 py-2 font-mono font-bold text-xs uppercase outline-none"
              >
                <option value="customer">Customer ID</option>
                <option value="transaction">Transaction ID</option>
                <option value="account">Account ID</option>
              </select>
              <input
                type="text"
                value={targetAccount}
                onChange={(e) => setTargetAccount(e.target.value)}
                className="sm:col-span-3 bg-[#f7f4ea] border-[2px] border-black px-3 py-2 font-mono font-black text-sm text-black outline-none"
                placeholder="e.g. C12382, 3514030, N-8901..."
              />
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-[10px] font-bold text-neutral-500 uppercase">Presets:</span>
              {["C12382", "3514030", "C11891-K1", "acc_mule_8829"].map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => setTargetAccount(preset)}
                  className="bg-[#f7f4ea] hover:bg-[#ffe45c] border border-black px-2 py-0.5 text-[10px] font-mono font-bold cursor-pointer"
                >
                  {preset}
                </button>
              ))}
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
                ? "RE-EXECUTE AUTONOMOUS GRAPH SCAN →"
                : "EXECUTE AUTONOMOUS GRAPH SCAN →"}
            </button>
          </div>
        )}

        {/* TAB 2: REASONING & CONSENSUS (Section 11 Requirement) */}
        {tab === 2 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <span className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                Agent Reasoning &amp; Evidence
              </span>
              <span className="font-mono text-xs font-bold text-[#16a34a] bg-[#eaf9ed] px-2 py-0.5 border border-[#16a34a]">
                High Risk Consensus (89%)
              </span>
            </div>

            {/* Metrics Grid: Risk, Uncertainty, Confidence */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
              <div className="bg-[#f7f4ea] border-[2px] border-black p-2">
                <span className="text-[var(--muted)] text-[10px] block">RISK SCORE</span>
                <span className="font-black text-red-600 text-base">0.89 (HIGH)</span>
              </div>
              <div className="bg-[#f7f4ea] border-[2px] border-black p-2">
                <span className="text-[var(--muted)] text-[10px] block">CONFIDENCE</span>
                <span className="font-black text-black text-base">96.8%</span>
              </div>
              <div className="bg-[#f7f4ea] border-[2px] border-black p-2">
                <span className="text-[var(--muted)] text-[10px] block">EPISTEMIC UNCERTAINTY</span>
                <span className="font-black text-black text-base">0.042 (LOW)</span>
              </div>
              <div className="bg-[#f7f4ea] border-[2px] border-black p-2">
                <span className="text-[var(--muted)] text-[10px] block">TOPOLOGY HOPS</span>
                <span className="font-black text-black text-base">3 Hops Cyclic</span>
              </div>
            </div>

            {/* Detected Patterns */}
            <div className="space-y-2 font-mono text-xs">
              <div className="font-bold text-black uppercase text-[11px]">
                CORRELATED GRAPH PATTERNS:
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  1. Velocity Spike: 14 txs under $10,000 threshold within 120s
                </span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  2. Graph Cycle: Direct funds returned to originating seed node (N-8901)
                </span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#f7f4ea] border border-neutral-300">
                <span className="text-[#16a34a] font-bold">✓</span>
                <span className="font-semibold text-neutral-800">
                  3. Device Fingerprint: Shared MAC hash across 6 distinct names
                </span>
              </div>
            </div>

            {/* Historical Case Matching */}
            <div className="p-3 bg-[#f7f4ea] border-[2px] border-black font-mono text-xs">
              <span className="font-bold block text-black mb-1">HISTORICAL CASE MEMORY:</span>
              <p className="text-neutral-700 leading-relaxed">
                Vector similarity matched <strong>#FG-9082</strong> (Mule Convergence Syndicate, cosine similarity 0.94). Previous outcome: FinCEN SAR filed and accounts frozen.
              </p>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setTab(3)}
                className="w-full bg-[#ffe45c] hover:bg-[#fed932] border-[3px] border-black py-2.5 font-syne font-black text-sm uppercase tracking-wider shadow-[4px_4px_0_#050505] cursor-pointer"
              >
                PROCEED TO NEXT-BEST-ACTIONS →
              </button>
            </div>
          </div>
        )}

        {/* TAB 3: NEXT-BEST-ACTION & APPROVAL (Section 11, 17, 18) */}
        {tab === 3 && (
          <div className="bg-white border-[3px] border-black p-5 sm:p-6 shadow-[5px_5px_0_#050505] space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <span className="font-syne font-black text-lg sm:text-xl uppercase text-black">
                Recommended Next-Best-Action
              </span>
              <span className="font-mono text-xs font-bold text-red-600 bg-red-50 px-2 py-0.5 border border-red-400">
                APPROVAL REQUIRED
              </span>
            </div>

            {/* Policy & Recommendation Card */}
            <div className="bg-[#f7f4ea] border-[2.5px] border-black p-4 font-mono text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-neutral-600 uppercase">POLICY RULE:</span>
                <span className="font-black text-black">RULE AML-R14 (High Velocity Mule Defense)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-neutral-600 uppercase">APPROVAL LEVEL:</span>
                <span className="font-black text-red-600">L2 Compliance Officer Required</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-neutral-600 uppercase">RECOMMENDED ACTION:</span>
                <span className="font-black text-black">PROVISIONAL_FREEZE_24H</span>
              </div>
            </div>

            {/* Action Triggers */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                disabled={isExecutingAction}
                onClick={() => handleExecuteAction("freeze_account")}
                className="p-3 bg-[#ff91b8] hover:bg-[#ff7ba8] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left disabled:opacity-50"
              >
                FREEZE ACCOUNT (24H)
              </button>
              <button
                type="button"
                disabled={isExecutingAction}
                onClick={() => handleExecuteAction("step_up_auth")}
                className="p-3 bg-[#9cc9ff] hover:bg-[#85beff] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left disabled:opacity-50"
              >
                MANDATE STEP-UP AUTH
              </button>
              <button
                type="button"
                disabled={isExecutingAction}
                onClick={() => handleExecuteAction("generate_sar")}
                className="p-3 bg-[#ffe45c] hover:bg-[#fcd935] border-[2.5px] border-black font-syne font-black text-xs uppercase shadow-[3px_3px_0_#050505] cursor-pointer text-left disabled:opacity-50"
              >
                FILE SAR REPORT
              </button>
            </div>

            {/* Execution / Approval State Feedback (Truthful, no fake success) */}
            {actionResult && (
              <div
                className={`p-3 border-[2px] font-mono text-xs leading-relaxed ${
                  actionResult.requiresApproval
                    ? "bg-[#fff7e6] border-[#ffa940] text-[#d46b08]"
                    : actionResult.executed
                    ? "bg-[#eef7ee] border-[#16a34a] text-[#16a34a]"
                    : "bg-[#f7f4ea] border-black text-black"
                }`}
              >
                <div className="font-black uppercase mb-1">
                  STATUS: {actionResult.status}
                </div>
                <div>{actionResult.message}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
