"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { benchmarkApi } from "@/lib/api";

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
      modelVersion: modelVersions.join(", ") || "N/A",
    };
  }, [report]);

  return (
    <div className="min-h-screen paper-texture p-4 sm:p-6">
      <div className="container mx-auto space-y-6">
        <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
          BACK TO FRAUDGRAPH CONSOLE
        </Link>

        <section className="brutal-card p-6 bg-white">
          <div className="tape-strip" />
          <span className="sticker sticker-yellow text-xs mb-2">BENCHMARK</span>
          <div className="mt-2 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="font-display text-4xl uppercase tracking-tight">
                HHGO ML Benchmark
              </h1>
              <p className="font-mono text-sm text-[var(--muted)] mt-1">
                Real model predictions from case_pack.csv. Official benchmark ground truth is hidden.
              </p>
            </div>
            <button
              type="button"
              onClick={() => void runBenchmark()}
              disabled={running}
              className="btn-primary px-4 py-2 text-xs"
            >
              {running ? "RUNNING..." : "RUN REAL BENCHMARK"}
            </button>
          </div>

          {loading ? (
            <div className="mt-6 border-[3px] border-black bg-[var(--paper)] p-4 font-mono text-sm">
              Loading benchmark report from FastAPI...
            </div>
          ) : error ? (
            <div className="mt-6 border-[3px] border-black bg-red-100 p-4 font-mono text-sm">
              {error}
            </div>
          ) : report && report.cases.length > 0 ? (
            <>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-4 mt-6">
                <div className="bg-[var(--paper)] border-[3px] border-black p-4">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">CASES</div>
                  <div className="font-display text-4xl text-[var(--mint-dark)]">{summary.total}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">ML FRAUD</div>
                  <div className="font-display text-4xl text-[var(--pink)]">{summary.predictedFraud}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">ML CLEAR</div>
                  <div className="font-display text-4xl text-[var(--blue)]">{summary.predictedClear}</div>
                </div>
                <div className="bg-[var(--paper)] border-[3px] border-black p-4">
                  <div className="font-mono text-xs font-bold text-[var(--muted)]">MODEL</div>
                  <div className="font-display text-2xl text-black">{summary.modelVersion}</div>
                </div>
              </div>

              <div className="mt-6 border-[3px] border-black bg-[var(--paper)] p-4 font-mono text-xs">
                {report.note}
              </div>

              <div className="mt-6 overflow-x-auto border-[3px] border-black bg-white">
                <table className="w-full min-w-[980px] border-collapse font-mono text-xs">
                  <thead className="bg-black text-white">
                    <tr>
                      <th className="p-3 text-left">Case</th>
                      <th className="p-3 text-left">Trigger</th>
                      <th className="p-3 text-left">Customer</th>
                      <th className="p-3 text-left">Card</th>
                      <th className="p-3 text-left">Transaction</th>
                      <th className="p-3 text-right">Bank Risk</th>
                      <th className="p-3 text-right">ML Probability</th>
                      <th className="p-3 text-left">ML Prediction</th>
                      <th className="p-3 text-right">Threshold</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.cases.map((item) => (
                      <tr key={item.case_id} className="border-t-[3px] border-black">
                        <td className="p-3 font-bold">{item.case_id}</td>
                        <td className="p-3">{item.trigger_type}</td>
                        <td className="p-3">{item.customer_id}</td>
                        <td className="p-3">{item.card_id}</td>
                        <td className="p-3">{item.transaction_id}</td>
                        <td className="p-3 text-right">{formatScore(item.bank_risk_score)}</td>
                        <td className="p-3 text-right">{formatScore(item.ml_probability)}</td>
                        <td className="p-3">{item.ml_prediction ? "fraud" : "clear"}</td>
                        <td className="p-3 text-right">{formatScore(item.threshold)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="mt-6 border-[3px] border-black bg-[var(--paper)] p-4 font-mono text-sm">
              No benchmark report is available yet. Run the benchmark to generate real ML predictions.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
