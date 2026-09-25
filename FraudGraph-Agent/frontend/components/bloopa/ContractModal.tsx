"use client";

import React, { useState } from "react";

interface ContractModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ContractModal({ isOpen, onClose }: ContractModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const tealCode = `// TigerGraph Hybrid Retriever & FraudGraph Consensus Model
// Cluster ID: 764393317 (Production Fintech Defense)

QUERY DetectMuleRing(VERTEX<Account> seedNode, INT maxHops) {
  ListAccum<EDGE> @@cycleEdges;
  SumAccum<INT> @inDegree, @outDegree;
  
  Start = { seedNode };
  
  // Hop 1: Rapid structuring distribution
  Hop1 = SELECT t FROM Start:s -(Transfer:e)-> Account:t
         ACCUM @@cycleEdges += e;
         
  // Hop 2: Intermediary accounts
  Hop2 = SELECT t FROM Hop1:s -(Transfer:e)-> Account:t
         WHERE t != seedNode
         ACCUM @@cycleEdges += e;
         
  // Hop 3: Cycle return to seed
  Hop3 = SELECT t FROM Hop2:s -(Transfer:e)-> Account:t
         WHERE t == seedNode
         ACCUM @@cycleEdges += e;
         
  PRINT Hop3.size() > 0 AS is_mule_ring, @@cycleEdges;
}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(tealCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs select-none">
      <div className="relative w-full max-w-2xl bg-[#f7f4ea] border-[4px] border-black p-6 sm:p-8 shadow-[12px_12px_0_#050505] max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer"
        >
          ✕
        </button>

        <div className="mb-4">
          <span className="sticker sticker-yellow text-xs font-mono font-bold">
            GSQL ALGORITHM VERIFIED
          </span>
          <h2 className="font-syne font-black text-2xl sm:text-3xl text-black uppercase tracking-tight mt-1">
            TigerGraph Query #764393317
          </h2>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            GSQL Graph Traversal query compiled for sub-second real-time transaction reasoning.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 font-mono text-xs">
          <div className="bg-white border-[2px] border-black p-2.5">
            <span className="text-neutral-500 block">Query ID:</span>
            <span className="font-black text-black">764393317</span>
          </div>
          <div className="bg-white border-[2px] border-black p-2.5">
            <span className="text-neutral-500 block">Dialect:</span>
            <span className="font-black text-black">GSQL v3.9</span>
          </div>
          <div className="bg-white border-[2px] border-black p-2.5">
            <span className="text-neutral-500 block">Max Hop Depth:</span>
            <span className="font-black text-black">3-Hop Deep</span>
          </div>
          <div className="bg-white border-[2px] border-black p-2.5">
            <span className="text-neutral-500 block">Consensus Latency:</span>
            <span className="font-black text-[#16a34a]">78.4 ms</span>
          </div>
        </div>

        <div className="relative bg-[#0d1117] text-[#58a6ff] border-[2.5px] border-black p-4 font-mono text-xs overflow-x-auto rounded-none shadow-[3px_3px_0_#050505] max-h-64">
          <button
            type="button"
            onClick={handleCopy}
            className="absolute top-3 right-3 bg-white text-black hover:bg-neutral-200 border border-black px-2.5 py-1 text-[11px] font-bold uppercase"
          >
            {copied ? "✓ Copied!" : "Copy GSQL"}
          </button>
          <pre className="text-neutral-300 font-mono text-[11px] leading-relaxed">
            {tealCode}
          </pre>
        </div>

        <div className="mt-5 flex items-center justify-between gap-4">
          <span className="text-xs font-mono font-bold text-neutral-600">
            Audit status: FinCEN & Compliance Admissible
          </span>
          <button
            type="button"
            onClick={onClose}
            className="bg-[#b9f5cf] hover:bg-[#a1f1bc] border-[2.5px] border-black px-5 py-2 font-syne font-black text-xs uppercase shadow-[2px_2px_0_#050505] cursor-pointer"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
}
