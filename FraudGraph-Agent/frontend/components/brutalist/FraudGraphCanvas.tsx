"use client";

import React, { useState } from "react";

export interface GraphNode {
  id: string;
  label: string;
  type: "mule" | "synthetic" | "crypto" | "victim" | "merchant";
  riskScore: number;
  x: number;
  y: number;
  volume: string;
  degree: number;
  centrality: number;
  flaggedReason: string;
}

export interface GraphEdge {
  from: string;
  to: string;
  amount: string;
  hops: number;
  isCycle?: boolean;
}

const INITIAL_NODES: GraphNode[] = [
  {
    id: "N-8901",
    label: "Mule Ring Hub #01",
    type: "mule",
    riskScore: 98,
    x: 320,
    y: 190,
    volume: "$1,820,400",
    degree: 8,
    centrality: 0.89,
    flaggedReason: "Rapid dispersion to 7 secondary accounts within 4 minutes",
  },
  {
    id: "N-3319",
    label: "Synthetic ID Alpha",
    type: "synthetic",
    riskScore: 94,
    x: 180,
    y: 110,
    volume: "$490,000",
    degree: 4,
    centrality: 0.65,
    flaggedReason: "SSN collision with 12 deceased individuals, forged utility bill",
  },
  {
    id: "N-4092",
    label: "Shell Corp Holdings",
    type: "mule",
    riskScore: 91,
    x: 480,
    y: 130,
    volume: "$2,100,000",
    degree: 6,
    centrality: 0.78,
    flaggedReason: "Incorporated 11 days ago; immediate multimillion inbound velocity",
  },
  {
    id: "N-7714",
    label: "Crypto Bridge 0x9f..4a",
    type: "crypto",
    riskScore: 88,
    x: 450,
    y: 310,
    volume: "$920,000",
    degree: 5,
    centrality: 0.72,
    flaggedReason: "Privacy mixer pool interaction detected via chain analysis",
  },
  {
    id: "N-2015",
    label: "Secondary Mule #04",
    type: "mule",
    riskScore: 82,
    x: 210,
    y: 290,
    volume: "$340,000",
    degree: 3,
    centrality: 0.54,
    flaggedReason: "Structured ATM cash-out clusters across 4 metropolitan ATMs",
  },
  {
    id: "N-1002",
    label: "Merchant POS Gateway",
    type: "merchant",
    riskScore: 42,
    x: 620,
    y: 220,
    volume: "$680,000",
    degree: 3,
    centrality: 0.38,
    flaggedReason: "Abnormal chargeback frequency spike (+410% in 48h)",
  },
  {
    id: "N-0041",
    label: "Victim Account (Compromised)",
    type: "victim",
    riskScore: 19,
    x: 80,
    y: 210,
    volume: "$185,000",
    degree: 2,
    centrality: 0.22,
    flaggedReason: "Account takeover via SIM-swap; credential stuffed login",
  },
];

const INITIAL_EDGES: GraphEdge[] = [
  { from: "N-0041", to: "N-3319", amount: "$185,000", hops: 1 },
  { from: "N-3319", to: "N-8901", amount: "$490,000", hops: 1, isCycle: true },
  { from: "N-8901", to: "N-4092", amount: "$850,000", hops: 2, isCycle: true },
  { from: "N-4092", to: "N-7714", amount: "$920,000", hops: 2 },
  { from: "N-8901", to: "N-2015", amount: "$340,000", hops: 1 },
  { from: "N-2015", to: "N-3319", amount: "$120,000", hops: 3, isCycle: true },
  { from: "N-4092", to: "N-1002", amount: "$310,000", hops: 2 },
];

export function FraudGraphCanvas({ onAction }: { onAction: (msg: string) => void }) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(INITIAL_NODES[0]);
  const [showCyclesOnly, setShowCyclesOnly] = useState(false);
  const [highRiskOnly, setHighRiskOnly] = useState(false);

  const filteredNodes = INITIAL_NODES.filter((n) => {
    if (highRiskOnly && n.riskScore < 85) return false;
    return true;
  });

  const filteredEdges = INITIAL_EDGES.filter((e) => {
    if (showCyclesOnly && !e.isCycle) return false;
    const hasFrom = filteredNodes.some((n) => n.id === e.from);
    const hasTo = filteredNodes.some((n) => n.id === e.to);
    return hasFrom && hasTo;
  });

  const getNodeColor = (type: GraphNode["type"]) => {
    switch (type) {
      case "mule":
        return "var(--red)";
      case "synthetic":
        return "var(--orange)";
      case "crypto":
        return "var(--pink)";
      case "merchant":
        return "var(--sky)";
      case "victim":
        return "var(--mint)";
      default:
        return "var(--yellow)";
    }
  };

  return (
    <div className="brutal-card p-4 sm:p-6 bg-white relative">
      <div className="tape-strip" />

      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b-[3px] border-black">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
              TIGERGRAPH TOPOLOGY EXPLORER
            </span>
            <span className="sticker sticker-yellow text-xs py-0.5 px-2">
              SYNDICATE #SR-901
            </span>
          </div>
          <p className="text-xs font-mono text-[var(--muted)] mt-1">
            Real-time sub-graph traversal · Cyclic flow detection · Pagerank centrality analysis
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setShowCyclesOnly(!showCyclesOnly)}
            className={`font-mono text-xs uppercase px-3 py-1.5 border-[2px] border-black transition-all ${
              showCyclesOnly
                ? "bg-[var(--pink)] shadow-[3px_3px_0_#050505] translate-x-[-1px] translate-y-[-1px]"
                : "bg-white hover:bg-[var(--yellow)]"
            }`}
          >
            {showCyclesOnly ? "● CYCLES ONLY [ON]" : "○ SHOW CYCLES"}
          </button>

          <button
            onClick={() => setHighRiskOnly(!highRiskOnly)}
            className={`font-mono text-xs uppercase px-3 py-1.5 border-[2px] border-black transition-all ${
              highRiskOnly
                ? "bg-[var(--red)] text-white shadow-[3px_3px_0_#050505] translate-x-[-1px] translate-y-[-1px]"
                : "bg-white hover:bg-[var(--yellow)]"
            }`}
          >
            {highRiskOnly ? "● HIGH RISK ONLY" : "○ ALL RISK LEVELS"}
          </button>

          <button
            onClick={() => {
              setSelectedNode(INITIAL_NODES[0]);
              setShowCyclesOnly(false);
              setHighRiskOnly(false);
              onAction("Graph reset to default view.");
            }}
            className="btn-ghost text-xs py-1.5 px-3"
          >
            RESET
          </button>
        </div>
      </div>

      {/* Main Grid: Interactive Canvas + Inspector Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Graph Canvas */}
        <div className="lg:col-span-8 bg-[var(--paper)] border-[3px] border-black shadow-[5px_5px_0_#050505] p-2 sm:p-4 relative min-h-[440px] overflow-hidden">
          {/* Subtle graph background grid */}
          <div className="absolute inset-0 graph-paper pointer-events-none opacity-70" />

          {/* Canvas SVG */}
          <svg className="w-full h-[420px] relative z-10" viewBox="0 0 720 420">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="18"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 8 3, 0 6" fill="#050505" />
              </marker>
              <marker
                id="arrowhead-cycle"
                markerWidth="8"
                markerHeight="6"
                refX="18"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 8 3, 0 6" fill="#ff6f61" />
              </marker>
            </defs>

            {/* Edges */}
            {filteredEdges.map((edge, idx) => {
              const fromNode = INITIAL_NODES.find((n) => n.id === edge.from);
              const toNode = INITIAL_NODES.find((n) => n.id === edge.to);
              if (!fromNode || !toNode) return null;

              const isHighlighted =
                selectedNode && (selectedNode.id === edge.from || selectedNode.id === edge.to);

              return (
                <g key={idx} className="cursor-pointer">
                  <line
                    x1={fromNode.x}
                    y1={fromNode.y}
                    x2={toNode.x}
                    y2={toNode.y}
                    stroke={edge.isCycle ? "#ff6f61" : "#050505"}
                    strokeWidth={isHighlighted ? 4 : edge.isCycle ? 3 : 2}
                    strokeDasharray={edge.isCycle ? "6,4" : "none"}
                    markerEnd={edge.isCycle ? "url(#arrowhead-cycle)" : "url(#arrowhead)"}
                  />
                  {/* Midpoint Amount Pill */}
                  <rect
                    x={(fromNode.x + toNode.x) / 2 - 28}
                    y={(fromNode.y + toNode.y) / 2 - 10}
                    width={56}
                    height={18}
                    fill={edge.isCycle ? "#ffe45c" : "#ffffff"}
                    stroke="#050505"
                    strokeWidth="1.5"
                    rx="2"
                  />
                  <text
                    x={(fromNode.x + toNode.x) / 2}
                    y={(fromNode.y + toNode.y) / 2 + 3}
                    textAnchor="middle"
                    fontFamily="JetBrains Mono"
                    fontSize="9"
                    fontWeight="800"
                    fill="#050505"
                  >
                    {edge.amount}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const nodeColor = getNodeColor(node.type);

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="cursor-pointer transition-transform hover:scale-110"
                >
                  {/* Hard Shadow Box */}
                  <rect
                    x="-24"
                    y="-24"
                    width="48"
                    height="48"
                    fill="#050505"
                    transform="translate(4, 4)"
                    rx="3"
                  />
                  {/* Primary Node Body */}
                  <rect
                    x="-24"
                    y="-24"
                    width="48"
                    height="48"
                    fill={nodeColor}
                    stroke="#050505"
                    strokeWidth={isSelected ? 4 : 3}
                    rx="3"
                  />
                  {/* Risk Badge Icon inside node */}
                  <text
                    x="0"
                    y="4"
                    textAnchor="middle"
                    fontFamily="Anton"
                    fontSize="13"
                    fill={node.type === "mule" ? "#ffffff" : "#050505"}
                  >
                    {node.riskScore}
                  </text>

                  {/* Node Label Below */}
                  <g transform="translate(0, 36)">
                    <rect
                      x="-65"
                      y="-11"
                      width="130"
                      height="20"
                      fill={isSelected ? "#050505" : "#ffffff"}
                      stroke="#050505"
                      strokeWidth="2"
                      rx="2"
                      filter="drop-shadow(2px 2px 0 #050505)"
                    />
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fontFamily="Inter"
                      fontSize="10"
                      fontWeight="800"
                      fill={isSelected ? "#ffffff" : "#050505"}
                    >
                      {node.label}
                    </text>
                  </g>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className="absolute bottom-2 left-2 right-2 bg-white/95 border-[2px] border-black p-2 flex flex-wrap items-center justify-between text-[11px] font-mono gap-2 z-20">
            <span className="font-bold">LEGEND:</span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3 h-3 bg-[var(--red)] border border-black inline-block" /> Mule Ring
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3 h-3 bg-[var(--orange)] border border-black inline-block" /> Synthetic ID
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3 h-3 bg-[var(--pink)] border border-black inline-block" /> Crypto Mixer
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-3 h-3 bg-[var(--mint)] border border-black inline-block" /> Victim
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="w-6 border-b-2 border-dashed border-[var(--red)] inline-block" /> Cyclic Smurfing Flow
            </span>
          </div>
        </div>

        {/* Node Inspector Docket Panel */}
        <div className="lg:col-span-4 bg-[var(--paper)] border-[3px] border-black shadow-[6px_6px_0_#050505] p-4 relative">
          <div className="tape-strip tape-strip-right" />
          <div className="border-b-[3px] border-black pb-2 mb-3">
            <span className="font-mono text-xs font-bold text-[var(--muted)]">VERTEX INSPECTOR</span>
            <h3 className="font-display text-2xl uppercase tracking-tight">
              {selectedNode ? selectedNode.label : "SELECT VERTEX"}
            </h3>
          </div>

          {selectedNode ? (
            <div className="space-y-4">
              {/* Risk Badge Bar */}
              <div className="flex items-center justify-between p-2.5 bg-white border-[2px] border-black">
                <span className="font-mono text-xs font-bold uppercase">FRAUD PROBABILITY</span>
                <span
                  className={`font-display text-xl px-2 py-0.5 border-[2px] border-black ${
                    selectedNode.riskScore > 85
                      ? "bg-[var(--red)] text-white"
                      : selectedNode.riskScore > 50
                      ? "bg-[var(--yellow)]"
                      : "bg-[var(--mint)]"
                  }`}
                >
                  {selectedNode.riskScore}% RISK
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="bg-white border-[2px] border-black p-2">
                  <div className="text-[var(--muted)]">VERTEX ID</div>
                  <div className="font-bold text-sm text-black">{selectedNode.id}</div>
                </div>
                <div className="bg-white border-[2px] border-black p-2">
                  <div className="text-[var(--muted)]">TOTAL VOLUME</div>
                  <div className="font-bold text-sm text-black">{selectedNode.volume}</div>
                </div>
                <div className="bg-white border-[2px] border-black p-2">
                  <div className="text-[var(--muted)]">GRAPH DEGREE</div>
                  <div className="font-bold text-sm text-black">{selectedNode.degree} Edges</div>
                </div>
                <div className="bg-white border-[2px] border-black p-2">
                  <div className="text-[var(--muted)]">CENTRALITY</div>
                  <div className="font-bold text-sm text-black">{selectedNode.centrality} PR</div>
                </div>
              </div>

              {/* TigerGraph Flagged Reason */}
              <div className="bg-white border-[2px] border-black p-3">
                <div className="font-mono text-[11px] font-bold uppercase text-[var(--muted)] mb-1">
                  DETECTION RATIONALE
                </div>
                <p className="text-xs font-semibold leading-relaxed">
                  {selectedNode.flaggedReason}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2">
                <button
                  onClick={() =>
                    onAction(`🚨 Vertex ${selectedNode.id} isolated: All outbound API transactions held.`)
                  }
                  className="btn-danger w-full text-xs py-2.5 justify-center shadow-[4px_4px_0_#050505]"
                >
                  ISOLATE VERTEX & FREEZE
                </button>
                <button
                  onClick={() =>
                    onAction(`🔍 Expanded TigerGraph k-hop subgraph query for ${selectedNode.id}.`)
                  }
                  className="btn-secondary w-full text-xs py-2 justify-center shadow-[4px_4px_0_#050505]"
                >
                  EXPAND K-HOP TRAVERSAL
                </button>
              </div>
            </div>
          ) : (
            <p className="font-mono text-xs text-[var(--muted)]">Click on any graph node to inspect vertices.</p>
          )}
        </div>
      </div>
    </div>
  );
}
