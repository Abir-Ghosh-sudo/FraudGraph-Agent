"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { casesApi, investigationsApi } from "@/lib/api";
import type { Case } from "@/types/case";

interface TerminalLine {
  prefix: ">" | "✓" | "⚠" | "!";
  text: string;
  tint?: "mint" | "yellow" | "pink" | "red" | "white";
}

const tintClass = {
  mint: "text-[var(--mint)]",
  yellow: "text-[var(--yellow)]",
  pink: "text-[var(--pink)]",
  red: "text-[var(--red)]",
  white: "text-white",
};

function buildScriptFromCase(c: Case): TerminalLine[] {
  const lines: TerminalLine[] = [
    { prefix: ">", text: "INVESTIGATION STARTED", tint: "mint" },
    { prefix: ">", text: `CASE: ${c.case_id.slice(0, 12).toUpperCase()}`, tint: "white" },
    { prefix: ">", text: `TRIGGER: ${c.title.slice(0, 30).toUpperCase()}`, tint: "white" },
    { prefix: ">", text: "", tint: "white" },
    { prefix: ">", text: `STATUS: ${c.status.toUpperCase()}`, tint: "yellow" },
  ];

  if (c.risk_score !== null && c.risk_score !== undefined) {
    const score = Math.round((c.risk_score as number) * 100);
    lines.push({
      prefix: ">",
      text: `RISK SCORE: ${score}%`,
      tint: score > 75 ? "red" : score > 50 ? "pink" : "yellow",
    });
  }

  if (c.risk_level) {
    lines.push({ prefix: ">", text: `RISK LEVEL: ${String(c.risk_level).toUpperCase()}`, tint: "white" });
  }

  lines.push({ prefix: ">", text: "", tint: "white" });

  if (c.evidence_ids.length > 0) {
    lines.push({ prefix: ">", text: `loading ${c.evidence_ids.length} evidence items...`, tint: "yellow" });
    lines.push({ prefix: "✓", text: `${c.evidence_ids.length} evidence records found`, tint: "mint" });
    lines.push({ prefix: ">", text: "", tint: "white" });
  }

  if (c.findings.length > 0) {
    lines.push({ prefix: ">", text: `analysing ${c.findings.length} findings...`, tint: "yellow" });
    for (const f of c.findings.slice(0, 3)) {
      lines.push({ prefix: "✓", text: f.title.slice(0, 50), tint: "mint" });
    }
    lines.push({ prefix: ">", text: "", tint: "white" });
  }

  if (c.decisions.length > 0) {
    lines.push({ prefix: ">", text: "evaluating decisions...", tint: "yellow" });
    for (const d of c.decisions.slice(0, 2)) {
      lines.push({ prefix: "✓", text: `DECISION: ${d.decision_type.toUpperCase()}`, tint: "mint" });
    }
    lines.push({ prefix: ">", text: "", tint: "white" });
  }

  if (c.actions.length > 0) {
    lines.push({ prefix: ">", text: "reviewing agent actions...", tint: "yellow" });
    for (const a of c.actions.slice(0, 2)) {
      lines.push({ prefix: "✓", text: `ACTION: ${a.action_type.toUpperCase()} [${a.status.toUpperCase()}]`, tint: "mint" });
    }
    lines.push({ prefix: ">", text: "", tint: "white" });
  }

  const statusLine =
    c.status === "resolved"
      ? { prefix: "✓" as const, text: "CASE RESOLVED", tint: "mint" as const }
      : c.status === "awaiting_approval"
      ? { prefix: "⚠" as const, text: "AWAITING ANALYST APPROVAL...", tint: "yellow" as const }
      : c.status === "escalated"
      ? { prefix: "!" as const, text: "CASE ESCALATED — PRIORITY HIGH", tint: "red" as const }
      : { prefix: ">" as const, text: "AGENT PIPELINE ACTIVE...", tint: "yellow" as const };

  lines.push(statusLine);

  return lines;
}

// Fallback demo script when no cases available
const DEMO_SCRIPT: TerminalLine[] = [
  { prefix: ">", text: "INVESTIGATION STARTED", tint: "mint" },
  { prefix: ">", text: "CASE: HHG-001", tint: "white" },
  { prefix: ">", text: "TRIGGER: FRAUD_SIGNAL", tint: "white" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "loading transaction...", tint: "yellow" },
  { prefix: "✓", text: "transaction found", tint: "mint" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "querying graph...", tint: "yellow" },
  { prefix: "✓", text: "12 connected entities", tint: "mint" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "searching historical cases...", tint: "yellow" },
  { prefix: "✓", text: "3 similar cases", tint: "mint" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "assessing risk...", tint: "yellow" },
  { prefix: ">", text: "MODEL: 0.91", tint: "pink" },
  { prefix: ">", text: "GRAPH: HIGH", tint: "pink" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "evaluating next-best-action...", tint: "yellow" },
  { prefix: "✓", text: "STEP_UP_AUTH", tint: "mint" },
  { prefix: ">", text: "", tint: "white" },
  { prefix: ">", text: "awaiting approval...", tint: "yellow" },
];

export function TerminalBlock() {
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [script, setScript] = useState<TerminalLine[]>(DEMO_SCRIPT);
  const [caseLabel, setCaseLabel] = useState("HHG-001");
  const endRef = useRef<HTMLDivElement>(null);
  const cancelRef = useRef(false);

  // Load real case data for terminal
  useEffect(() => {
    async function loadCase() {
      try {
        const cases = await casesApi.list<Case[]>();
        const arr = Array.isArray(cases) ? cases : [];
        // Pick most recently updated active case
        const active = arr
          .filter((c) => !["resolved", "closed"].includes(c.status))
          .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());

        if (active.length > 0) {
          const c = active[0];
          setScript(buildScriptFromCase(c));
          setCaseLabel(c.case_id.slice(0, 12).toUpperCase());
        }
      } catch {
        // Keep demo script
      }
    }
    void loadCase();
  }, []);

  // Typewriter effect runner
  const runScript = useCallback((scriptLines: TerminalLine[]) => {
    cancelRef.current = false;
    let lineIndex = 0;
    let charIndex = 0;
    let buffer: TerminalLine[] = [];

    const step = () => {
      if (cancelRef.current) return;
      if (lineIndex >= scriptLines.length) {
        lineIndex = 0;
        buffer = [];
        setLines([]);
        setTimeout(step, 1500);
        return;
      }

      const current = scriptLines[lineIndex];
      if (charIndex < current.text.length) {
        charIndex++;
        const partial = { ...current, text: current.text.slice(0, charIndex) };
        buffer = [...buffer.slice(0, lineIndex), partial];
        setLines([...buffer]);
        setTimeout(step, 28);
      } else {
        buffer = [...buffer.slice(0, lineIndex), current];
        setLines([...buffer]);
        lineIndex++;
        charIndex = 0;
        setTimeout(step, 320);
      }
    };

    const timer = setTimeout(step, 400);
    return () => {
      cancelRef.current = true;
      clearTimeout(timer);
    };
  }, []);

  useEffect(() => {
    const cleanup = runScript(script);
    return () => {
      cancelRef.current = true;
      cleanup?.();
    };
  }, [script, runScript]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="brutal-card bg-black p-4 sm:p-6 relative">
      <div className="tape-strip" />
      <div className="flex items-center justify-between mb-3 border-b-[3px] border-white/20 pb-2">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[var(--red)] border border-black" />
          <span className="w-3 h-3 rounded-full bg-[var(--yellow)] border border-black" />
          <span className="w-3 h-3 rounded-full bg-[var(--mint)] border border-black" />
        </div>
        <span className="font-mono text-xs font-bold text-white/70 uppercase">
          AGENT TERMINAL // {caseLabel}
        </span>
      </div>
      <div className="font-mono text-xs sm:text-sm leading-relaxed overflow-y-auto max-h-[320px] pr-2">
        {lines.map((line, idx) => (
          <div key={idx} className="flex items-start gap-2">
            <span className={tintClass[line.tint || "white"]}>
              {line.prefix}
            </span>
            <span className={tintClass[line.tint || "white"]}>{line.text}</span>
          </div>
        ))}
        <span className="inline-block w-2 h-4 bg-[var(--mint)] animate-pulse ml-3" />
        <div ref={endRef} />
      </div>
    </div>
  );
}