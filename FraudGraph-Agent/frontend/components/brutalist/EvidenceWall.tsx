"use client";

import React from "react";

interface EvidenceItem {
  id: string;
  type: "TRANSACTION" | "DEVICE" | "IP" | "HISTORY" | "CUSTOMER" | "CARD";
  title: string;
  value: string;
  subtitle?: string;
  tint?: "blue" | "yellow" | "pink" | "mint";
  rotation?: number;
}

const tintClass = {
  blue: "bg-[var(--sky)]",
  yellow: "bg-[var(--yellow)]",
  pink: "bg-[var(--pink)]",
  mint: "bg-[var(--mint)]",
};

export function EvidenceWall({ items }: { items: EvidenceItem[] }) {
  return (
    <div className="brutal-card card-paper p-5 sm:p-6 relative">
      <div className="tape-strip" />
      <div className="flex items-center justify-between mb-4 border-b-[3px] border-black pb-2">
        <div>
          <span className="sticker sticker-sky text-xs">EVIDENCE BOARD</span>
          <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight mt-1">
            INVESTIGATION EVIDENCE WALL
          </h2>
        </div>
        <span className="font-mono text-xs font-bold text-[var(--muted)]">
          {items.length} ITEMS PINNED
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item) => (
          <div
            key={item.id}
            className={`border-[3px] border-black p-4 relative ${tintClass[item.tint || "blue"]}`}
            style={{ transform: `rotate(${item.rotation || 0}deg)` }}
          >
            <div className="absolute -top-3 left-3">
              <span className="font-mono text-[10px] font-black uppercase px-2 py-0.5 bg-black text-white border-[2px] border-black">
                {item.type}
              </span>
            </div>
            <div className="mt-2">
              <div className="font-mono text-[11px] font-bold text-black/60 uppercase">
                {item.title}
              </div>
              <div className="font-display text-xl sm:text-2xl mt-1 leading-tight">
                {item.value}
              </div>
              {item.subtitle && (
                <div className="font-mono text-xs font-bold text-black/70 mt-2 pt-2 border-t-[2px] border-black/30">
                  {item.subtitle}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface DefaultEvidenceSetProps {
  onAction?: (msg: string) => void;
}

export function DefaultEvidenceWall({ onAction }: DefaultEvidenceSetProps) {
  const items: EvidenceItem[] = [
    {
      id: "tx-1",
      type: "TRANSACTION",
      title: "AMOUNT",
      value: "$842.19",
      subtitle: "NEW DEVICE",
      tint: "blue",
      rotation: -1,
    },
    {
      id: "dev-1",
      type: "DEVICE",
      title: "DEVICE ID",
      value: "DEVICE-7782",
      subtitle: "SHARED BY 4 CUSTOMERS",
      tint: "yellow",
      rotation: 1.5,
    },
    {
      id: "ip-1",
      type: "IP",
      title: "IP ADDRESS",
      value: "192.168.x.x",
      subtitle: "CONNECTED TO 7 ACCOUNTS",
      tint: "pink",
      rotation: -0.8,
    },
    {
      id: "hist-1",
      type: "HISTORY",
      title: "MATCHES",
      value: "3 SIMILAR CASES",
      subtitle: "PATTERN CONFIRMED",
      tint: "mint",
      rotation: 0.6,
    },
    {
      id: "cust-1",
      type: "CUSTOMER",
      title: "CUSTOMER ID",
      value: "C12382",
      subtitle: "HIGH RISK SCORE 0.91",
      tint: "blue",
      rotation: 0.4,
    },
    {
      id: "card-1",
      type: "CARD",
      title: "CARD TYPE",
      value: "VISA •••• 4821",
      subtitle: "CARD NOT PRESENT",
      tint: "yellow",
      rotation: -1.2,
    },
  ];

  return (
    <EvidenceWall
      items={items}
    />
  );
}