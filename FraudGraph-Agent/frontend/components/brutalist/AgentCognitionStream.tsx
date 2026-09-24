"use client";

import React, { useState } from "react";

export interface AgentStep {
  id: string;
  agent: string;
  role: string;
  status: "completed" | "active" | "queued";
  time: string;
  thought: string;
  tag: string;
  tagColor: string;
}

const INITIAL_STEPS: AgentStep[] = [
  {
    id: "step-1",
    agent: "TRIGGER NODE",
    role: "Transaction Intake & Velocity Filter",
    status: "completed",
    time: "02:14:02.119",
    thought:
      "Received batch #TX-98441 from Wire Clearinghouse. 4 anomalous wire transfers exceeding $250k each from freshly provisioned accounts.",
    tag: "TRIGGERED",
    tagColor: "var(--yellow)",
  },
  {
    id: "step-2",
    agent: "EVIDENCE COLLECTOR",
    role: "TigerGraph 3-Hop Traversal & Document Store",
    status: "completed",
    time: "02:14:02.348",
    thought:
      "Executed GSQL query `find_mule_cycles(start_vertex='N-8901', max_depth=3)`. Retrieved 14 interconnected vertices, 2 shared device fingerprints (IMEI #3901..), and 1 synthetic ID match in AML watchlist.",
    tag: "14 VERTICES",
    tagColor: "var(--sky)",
  },
  {
    id: "step-3",
    agent: "PATTERN RECOGNIZER",
    role: "Graph Topological Ring Classifier",
    status: "active",
    time: "02:14:02.610",
    thought:
      "Detected high-confidence Smurfing Ring topology. Money dispersal ratio: 1 -> 7 accounts within 240 seconds, followed by consolidation into offshore crypto gateway 0x9f..4a. Pattern Confidence: 96.8%.",
    tag: "RING DETECTED",
    tagColor: "var(--red)",
  },
  {
    id: "step-4",
    agent: "UNCERTAINTY ASSESSOR",
    role: "Bayesian Epistemic & Aleatoric Bounds",
    status: "queued",
    time: "02:14:02.820",
    thought:
      "Evaluating false-positive hazard against legitimate merchant payroll distribution. Epistemic uncertainty: 0.042 (Extremely Low).",
    tag: "EVALUATING",
    tagColor: "var(--lavender)",
  },
  {
    id: "step-5",
    agent: "ACTION RECOMMENDER",
    role: "Human-in-the-Loop Consensus",
    status: "queued",
    time: "02:14:03.010",
    thought:
      "Synthesizing Next Best Actions: (1) Immediate provisional freeze on 7 primary accounts, (2) Auto-generate FinCEN Suspicious Activity Report (SAR), (3) Alert destination crypto gateway.",
    tag: "PENDING CONSENSUS",
    tagColor: "var(--mint)",
  },
];

export function AgentCognitionStream({ onAction }: { onAction: (msg: string) => void }) {
  const [steps, setSteps] = useState<AgentStep[]>(INITIAL_STEPS);
  const [progress, setProgress] = useState(68);
  const [isStreaming, setIsStreaming] = useState(true);

  const handleStepForward = () => {
    setProgress((prev) => Math.min(100, prev + 15));
    onAction("Agent step executed: Pattern Classifier confirmed cycle consensus.");
  };

  const handleInjectEvent = () => {
    const newStep: AgentStep = {
      id: `step-${Date.now()}`,
      agent: "ANOMALY INJECTOR",
      role: "Real-time Telemetry Monitor",
      status: "active",
      time: new Date().toLocaleTimeString(),
      thought:
        "High-velocity withdrawal attempt caught at ATM-NY-421. Account #N-2015 attempted $10,000 cash dispersion. TigerGraph path blocked.",
      tag: "INTRUSION BLOCKED",
      tagColor: "var(--pink)",
    };
    setSteps([newStep, ...steps]);
    onAction("⚡ New anomaly event injected into multi-agent cognition stream!");
  };

  return (
    <div className="brutal-card p-4 sm:p-6 bg-white relative">
      <div className="tape-strip" />

      {/* Stream Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b-[3px] border-black">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
              AGENT COGNITION STREAM
            </h2>
            <span className="status">
              <span className="status-dot-live" />
              <span>CONSENSUS ENGINE : ACTIVE</span>
            </span>
          </div>
          <p className="text-xs font-mono text-[var(--muted)] mt-1">
            Real-time LangGraph multi-agent traversal telemetry · TigerGraph graph RAG reasoning
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`font-mono text-xs uppercase px-3 py-1.5 border-[2px] border-black transition-all ${
              isStreaming ? "bg-[var(--mint)]" : "bg-[var(--yellow)]"
            } shadow-[2px_2px_0_#050505]`}
          >
            {isStreaming ? "● LIVE STREAMING" : "❚❚ STREAM PAUSED"}
          </button>
          <button
            onClick={handleStepForward}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            STEP AGENT →
          </button>
          <button
            onClick={handleInjectEvent}
            className="btn-warning text-xs py-1.5 px-3"
          >
            + INJECT ANOMALY
          </button>
        </div>
      </div>

      {/* Brutalist Progress Indicator */}
      <div className="my-4 p-3 bg-[var(--paper)] border-[2px] border-black">
        <div className="flex items-center justify-between text-xs font-mono font-bold mb-2">
          <span>CONSENSUS FORMATION PROGRESS</span>
          <span className="bg-[var(--ink)] text-white px-2 py-0.5 font-display text-sm tracking-wider">
            {progress}% VERIFIED
          </span>
        </div>
        <div className="brutal-progress-outer">
          <div className="brutal-progress-bar" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--muted)] mt-1.5">
          <span>[████████░░░░░░░░] AGENT COGNITION ACTIVE</span>
          <span>EST. CONVERGENCE: 42ms</span>
        </div>
      </div>

      {/* Step Cards List */}
      <div className="space-y-3 mt-4">
        {steps.map((step, idx) => (
          <div
            key={step.id}
            className={`border-[3px] border-black p-4 relative transition-all ${
              step.status === "active"
                ? "bg-[var(--paper)] shadow-[6px_6px_0_#050505] translate-x-[2px]"
                : step.status === "completed"
                ? "bg-white shadow-[3px_3px_0_#050505]"
                : "bg-white/60 opacity-75 border-dashed"
            }`}
          >
            {/* Header info */}
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-1 border-b-[2px] border-black/20">
              <div className="flex items-center gap-2">
                <span className="font-display text-lg tracking-tight uppercase">
                  {step.agent}
                </span>
                <span className="font-mono text-xs text-[var(--muted)]">({step.role})</span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className="font-mono text-xs font-black uppercase px-2 py-0.5 border-[2px] border-black"
                  style={{ backgroundColor: step.tagColor }}
                >
                  {step.tag}
                </span>
                <span className="font-mono text-[11px] text-[var(--muted)]">{step.time}</span>
              </div>
            </div>

            {/* Thought log */}
            <p className="font-mono text-xs sm:text-sm font-semibold text-black leading-relaxed">
              {step.thought}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
