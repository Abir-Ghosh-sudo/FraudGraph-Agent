"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { benchmarkApi } from "@/lib/api";
import { Navbar } from "@/components/brutalist/Navbar";
import { StatusStrip, BottomStatus } from "@/components/brutalist/StatusBars";
import { ProtocolModal } from "@/components/bloopa/ProtocolModal";
import { GraphExplorerModal } from "@/components/graph/GraphExplorerModal";

type BenchmarkCase = {
  case_id: string;
  trigger_type: string;
  customer_id: string;
  card_id: string;
  transaction_id: string;
  bank_risk_score: number | null;
  ml_probability: number;
  ml_prediction: boolean;
  threshold: number;
  model_version: string | null;
  investigation_status?: string;
  recommended_action?: string;
  execution_approval_state?: string;
};

type BenchmarkReport = {
  benchmark_cases: number;
  ground_truth_available: boolean;
  note: string;
  cases: BenchmarkCase[];
  output_reference?: string;
};

function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return value.toFixed(3);
}

export default function BenchmarkPage() {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState("C12382");

  async function loadReport() {
    setLoading(true);
    setError(null);

    try {
      setReport(await benchmarkApi.get<BenchmarkReport>());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load benchmark report.");
    } finally {
      setLoading(false);
    }
  }

  async function runBenchmark() {
    setRunning(true);
    setError(null);

    try {
      setReport(await benchmarkApi.run<BenchmarkReport>());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run benchmark.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    void loadReport();
  }, []);

  const summary = useMemo(() => {
    const cases = report?.cases ?? [];
    const predictedFraud = cases.filter((item) => item.ml_prediction).length;
    const modelVersions = Array.from(
      new Set(cases.map((item) => item.model_version).filter(Boolean)),
    );

    return {
      total: cases.length,
      predictedFraud,
      predictedClear: cases.length - predictedFraud,
      modelVersion: modelVersions.join(", ") || "XGBoost v1.4",
    };
  }, [report]);

  return (
    <div className="min-h-screen paper-texture flex flex-col selection:bg-[var(--yellow)] selection:text-black">
      <StatusStrip />
      <Navbar
        activeTab="benchmark"
        onOpenNewCase={() => setConsoleOpen(true)}
        onOpenGraph={() => setGraphModalOpen(true)}
      />

      <main className="container mx-auto px-4 sm:px-6 py-6 flex-1 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
            ← BACK TO FRAUDGRAPH CONSOLE
          </Link>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setSelectedTarget("C12382");
                setGraphModalOpen(true);
              }}
              className="bg-[#ffe45c] hover:bg-[#fed932] border-[2.5px] border-black px-3.5 py-1.5 font-mono font-bold text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
            >
              EXPLORE GRAPH →
            </button>
            <button
              type="button"
              onClick={() => void runBenchmark()}
              disabled={running}
              className="btn-primary text-xs py-1.5 px-4 cursor-pointer disabled:opacity-60"
            >
              {running ? "EVALUATING MODEL..." : "RUN REAL BENCHMARK →"}
            </button>
          </div>
        </div>

        <section className="brutal-card p-6 bg-white relative">
          <div className="tape-strip" />
          <div className="flex items-center gap-2 flex-wrap mb-2">
            <span className="sticker sticker-yellow text-xs font-mono font-bold">
              BENCHMARK EVALUATION
            </span>
            <span className="bg-[#ff9aa8] text-black border-[2px] border-black px-2 py-0.5 font-mono text-[10px] font-black uppercase">
              OFFICIAL GROUND TRUTH NOT AVAILABLE
            </span>
          </div>

          <div className="mt-2 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="font-display text-3xl sm:text-4xl uppercase tracking-tight text-black">
                HHGO ML Fraud Benchmark (HHG-001 – HHG-020)
              </h1>
              <p className="font-mono text-xs sm:text-sm text-[var(--muted)] mt-1 font-semibold">
                Real model inferences scored against case_pack.csv. Hidden competition ground truth remains strictly protected.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="mt-6 border-[3px] border-black bg-[var(--paper)] p-6 font-mono text-sm text-center">
              <div className="inline-block w-8 h-8 border-3 border-black border-t-[#ffe45c] rounded-full animate-spin mb-2" />
              <div>Loading benchmark report from FastAPI backend...</div>
            </div>
          ) : error ? (
            <div className="mt-6 border-[3px] border-black bg-red-100 p-4 font-mono text-xs font-bold text-red-800">
              {error}
            </div>
          ) : report && report.cases.length > 0 ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="bg-[var(--paper)] border-[3px] border-black p-4 shadow-[3px_3px_0_#050505]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">TOTAL CASES</div>
                  <div className="font-display text-3xl sm:text-4xl text-[var(--mint-dark)]">{summary.total}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4 shadow-[3px_3px_0_#050505]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">PREDICTED FRAUD</div>
                  <div className="font-display text-3xl sm:text-4xl text-[var(--pink)]">{summary.predictedFraud}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4 shadow-[3px_3px_0_#050505]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">PREDICTED CLEAR</div>
                  <div className="font-display text-3xl sm:text-4xl text-[var(--blue)]">{summary.predictedClear}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4 shadow-[3px_3px_0_#050505]">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">MODEL ARTIFACT</div>
                  <div className="font-syne font-black text-xl text-black truncate">{summary.modelVersion}</div>
                </div>
              </div>

              <div className="mt-6 border-[3px] border-black bg-[#f7f4ea] p-4 font-mono text-xs font-semibold">
                <strong>NOTE:</strong> {report.note || "OFFICIAL GROUND TRUTH NOT AVAILABLE. Predictions represent live model scores against feature vectors."}
              </div>

              {/* Table (Section 19: All 10 required fields per case) */}
              <div className="mt-6 overflow-x-auto border-[3px] border-black bg-white shadow-[4px_4px_0_#050505]">
                <table className="w-full min-w-[1050px] border-collapse font-mono text-xs">
                  <thead className="bg-black text-white">
                    <tr>
                      <th className="p-3 text-left">Case ID</th>
                      <th className="p-3 text-left">Trigger</th>
                      <th className="p-3 text-left">Customer</th>
                      <th className="p-3 text-left">Card</th>
                      <th className="p-3 text-left">Transaction</th>
                      <th className="p-3 text-right">Bank Risk</th>
                      <th className="p-3 text-right">ML Prob</th>
                      <th className="p-3 text-left">Status</th>
                      <th className="p-3 text-left">Recommended Action</th>
                      <th className="p-3 text-left">Approval State</th>
                      <th className="p-3 text-center">Graph</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.cases.map((item) => {
                      const isHigh = item.ml_prediction || (item.ml_probability > 0.5);
                      const recAction = item.recommended_action || (isHigh ? "BLOCK_CARD" : "ALLOW_TRANSACTION");
                      const approvalState = item.execution_approval_state || (isHigh ? "APPROVAL REQUIRED" : "AUTO_CLEARED");
                      const status = item.investigation_status || (isHigh ? "INVESTIGATING" : "MONITORING");

                      return (
                        <tr key={item.case_id} className="border-t-[2px] border-black hover:bg-[#f7f4ea] transition-colors">
                          <td className="p-3 font-black">{item.case_id}</td>
                          <td className="p-3">{item.trigger_type}</td>
                          <td className="p-3 font-bold">{item.customer_id}</td>
                          <td className="p-3">{item.card_id}</td>
                          <td className="p-3">{item.transaction_id}</td>
                          <td className="p-3 text-right">{formatScore(item.bank_risk_score)}</td>
                          <td className={`p-3 text-right font-black ${isHigh ? "text-red-600" : "text-green-700"}`}>
                            {formatScore(item.ml_probability)}
                          </td>
                          <td className="p-3 font-bold">{status}</td>
                          <td className="p-3 font-bold">
                            <span className={`px-2 py-0.5 border border-black ${isHigh ? "bg-[#ffe45c]" : "bg-[#b9f5cf]"}`}>
                              {recAction}
                            </span>
                          </td>
                          <td className="p-3">
                            <span className={`px-1.5 py-0.5 text-[10px] font-bold ${isHigh ? "text-red-600 bg-red-50 border border-red-300" : "text-neutral-600"}`}>
                              {approvalState}
                            </span>
                          </td>
                          <td className="p-3 text-center">
                            <button
                              type="button"
                              onClick={() => {
                                setSelectedTarget(item.customer_id || item.transaction_id);
                                setGraphModalOpen(true);
                              }}
                              className="px-2 py-1 bg-white hover:bg-[#ffe45c] border border-black text-[10px] font-bold uppercase shadow-[1px_1px_0_#050505] cursor-pointer"
                            >
                              VIEW
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="mt-6 border-[3px] border-black bg-[var(--paper)] p-6 font-mono text-sm flex flex-col items-center gap-3 text-center">
              <div>No pre-computed benchmark report is available yet.</div>
              <button
                type="button"
                onClick={() => void runBenchmark()}
                className="btn-primary text-xs py-2 px-5 cursor-pointer"
              >
                RUN BENCHMARK EVALUATION (HHG-001 – HHG-020) →
              </button>
            </div>
          )}
        </section>
      </main>

      <BottomStatus />

      {/* Modals */}
      <GraphExplorerModal
        isOpen={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        initialTarget={selectedTarget}
      />

      <ProtocolModal
        isOpen={consoleOpen}
        onClose={() => setConsoleOpen(false)}
      />
    </div>
  );
}
