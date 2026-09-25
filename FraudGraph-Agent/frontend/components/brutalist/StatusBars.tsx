"use client";

import React, { useEffect, useState } from "react";
import { useHealthStatus } from "@/hooks/use-dashboard";

export function StatusStrip() {
  const [now, setNow] = useState<string>("");
  const { health } = useHealthStatus(10000);

  useEffect(() => {
    const tick = () => {
      setNow(
        new Date()
          .toLocaleTimeString("en-GB", { hour12: false })
          .replace(":", ":"),
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="w-full bg-black text-white font-mono text-[11px] sm:text-[12px] tracking-wider uppercase border-b-[3px] border-black">
      <div className="container mx-auto px-4 sm:px-6 py-1.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3 sm:gap-5 flex-wrap">
          <span className="inline-flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full border border-white ${
                health.backendOnline ? "bg-[var(--mint)] status-dot-live" : "bg-[var(--red)]"
              }`}
            />
            FRAUDGRAPH AGENT
          </span>
          <span className="hidden sm:inline-flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 inline-block ${health.agent ? "bg-[var(--mint)]" : "bg-[var(--red)]"}`} />
            {health.agent ? "AI INVESTIGATION ENGINE ONLINE" : "AI ENGINE OFFLINE"}
          </span>
          <span className="hidden md:inline-flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 inline-block ${health.graph ? "bg-[var(--mint)]" : "bg-[var(--yellow)]"}`} />
            {health.graph ? "GRAPH CONNECTED" : "GRAPH UNCONFIGURED"}
          </span>
          <span className="hidden lg:inline-flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 inline-block ${health.model ? "bg-[var(--mint)]" : "bg-[var(--yellow)]"}`} />
            {health.model ? "MODEL ONLINE" : "MODEL UNCONFIGURED"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[var(--yellow)] font-bold">{now || "00:00:00"}</span>
          <span className="hidden sm:inline-flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 inline-block ${health.engine ? "bg-[var(--mint)]" : "bg-[var(--red)]"}`} />
            {health.backendOnline ? "CASE ENGINE →" : "BACKEND OFFLINE"}
          </span>
        </div>
      </div>
    </div>
  );
}

export function BottomStatus() {
  const { health } = useHealthStatus(10000);

  const statuses = [
    { label: "AGENT", ok: health.agent, pulse: health.agent },
    { label: "TIGERGRAPH", ok: health.graph, pulse: health.graph },
    { label: "MODEL", ok: health.model, pulse: false },
    { label: "LANGGRAPH", ok: health.engine, pulse: false },
  ];

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t-[3px] border-black shadow-[0_-6px_0_#050505]">
      <div className="container mx-auto px-4 sm:px-6 py-2 flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] sm:text-[12px] font-bold uppercase tracking-wider">
        <div className="flex items-center gap-4 flex-wrap">
          {statuses.map((s) => (
            <span key={s.label} className="inline-flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full border border-black ${
                  s.ok ? "bg-[var(--mint)]" : "bg-[var(--red)]"
                } ${s.pulse ? "status-dot-live" : ""}`}
              />
              {s.label}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="font-display text-base sm:text-lg tracking-tight">
            FRAUDGRAPH
          </span>
          <span className="text-[var(--muted)] normal-case font-medium">
            © 2026 AUTONOMOUS FRAUD DEFENSE
          </span>
        </div>
      </div>
    </footer>
  );
}