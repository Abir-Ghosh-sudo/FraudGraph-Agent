"use client";

import React, { useState } from "react";

export interface Transaction {
  id: string;
  timestamp: string;
  sender: string;
  recipient: string;
  amount: string;
  type: string;
  riskScore: number;
  status: "FLAGGED" | "CLEARED" | "HELD" | "REVIEW";
}

const TRANSACTIONS_DATA: Transaction[] = [
  {
    id: "TX-99401",
    timestamp: "02:14:18",
    sender: "N-8901 (Mule Hub Alpha)",
    recipient: "N-4092 (Shell Corp)",
    amount: "$850,000",
    type: "CROSS-BORDER WIRE",
    riskScore: 98,
    status: "FLAGGED",
  },
  {
    id: "TX-99402",
    timestamp: "02:13:52",
    sender: "N-3319 (Synthetic ID)",
    recipient: "N-8901 (Mule Hub Alpha)",
    amount: "$490,000",
    type: "ACH BATCH TRANSFER",
    riskScore: 94,
    status: "HELD",
  },
  {
    id: "TX-99403",
    timestamp: "02:12:44",
    sender: "N-4092 (Shell Corp)",
    recipient: "0x9f..4a (Crypto Bridge)",
    amount: "$920,000",
    type: "SWIFT WIRE (OFFSHORE)",
    riskScore: 91,
    status: "FLAGGED",
  },
  {
    id: "TX-99404",
    timestamp: "02:10:19",
    sender: "N-0041 (Victim Account)",
    recipient: "N-3319 (Synthetic ID)",
    amount: "$185,000",
    type: "INSTANT FEDNOW",
    riskScore: 89,
    status: "HELD",
  },
  {
    id: "TX-99405",
    timestamp: "02:08:33",
    sender: "N-1002 (Merchant POS)",
    recipient: "N-8901 (Mule Hub Alpha)",
    amount: "$310,000",
    type: "SETTLEMENT REVERSAL",
    riskScore: 78,
    status: "REVIEW",
  },
  {
    id: "TX-99406",
    timestamp: "02:05:01",
    sender: "Acme Payroll Service",
    recipient: "Employee Direct Dep",
    amount: "$4,250",
    type: "DOMESTIC ACH",
    riskScore: 6,
    status: "CLEARED",
  },
  {
    id: "TX-99407",
    timestamp: "02:02:40",
    sender: "Global Logistics AG",
    recipient: "Port Customs Fee",
    amount: "$32,800",
    type: "WIRE TRANSFER",
    riskScore: 12,
    status: "CLEARED",
  },
];

export function TransactionLedger({
  onInspect,
  onShowToast,
}: {
  onInspect: (tx: Transaction) => void;
  onShowToast: (msg: string) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");

  const filtered = TRANSACTIONS_DATA.filter((tx) => {
    if (filterStatus !== "ALL" && tx.status !== filterStatus) return false;
    if (
      searchTerm &&
      !tx.id.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !tx.sender.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !tx.recipient.toLowerCase().includes(searchTerm.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  return (
    <div className="brutal-card p-4 sm:p-6 bg-white relative">
      <div className="tape-strip" />

      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b-[3px] border-black">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-display text-2xl sm:text-3xl uppercase tracking-tight">
              REAL-TIME TRANSACTION LEDGER
            </h2>
            <span className="sticker sticker-mint text-xs py-0.5 px-2">
              LIVE FEED
            </span>
          </div>
          <p className="text-xs font-mono text-[var(--muted)] mt-1">
            Real-time ingestion · Graph feature computation · Fraud score inference
          </p>
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {["ALL", "FLAGGED", "HELD", "REVIEW", "CLEARED"].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`font-mono text-xs font-bold px-2.5 py-1 border-[2px] border-black transition-all ${
                filterStatus === status
                  ? "bg-[var(--mint)] shadow-[2px_2px_0_#050505] translate-x-[-1px] translate-y-[-1px]"
                  : "bg-white hover:bg-[var(--yellow)] shadow-none"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input */}
      <div className="my-4">
        <input
          type="text"
          placeholder="SEARCH BY TRANSACTION ID, SENDER, OR RECIPIENT..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="brutal-input text-xs sm:text-sm uppercase placeholder:normal-case placeholder:font-mono"
        />
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto border-[3px] border-black shadow-[4px_4px_0_#050505]">
        <table className="brutal-table">
          <thead>
            <tr>
              <th>TX ID</th>
              <th>TIME</th>
              <th>SENDER</th>
              <th>RECIPIENT</th>
              <th>AMOUNT</th>
              <th>RISK</th>
              <th>STATUS</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((tx) => (
              <tr key={tx.id}>
                <td className="font-mono font-bold text-xs">{tx.id}</td>
                <td className="font-mono text-xs text-[var(--muted)]">{tx.timestamp}</td>
                <td className="font-mono text-xs font-semibold">{tx.sender}</td>
                <td className="font-mono text-xs font-semibold">{tx.recipient}</td>
                <td className="font-mono font-bold text-xs sm:text-sm">{tx.amount}</td>
                <td>
                  <span
                    className={`font-mono font-black text-xs px-2 py-0.5 border-[2px] border-black ${
                      tx.riskScore > 85
                        ? "bg-[var(--red)] text-white"
                        : tx.riskScore > 50
                        ? "bg-[var(--yellow)] text-black"
                        : "bg-[var(--mint)] text-black"
                    }`}
                  >
                    {tx.riskScore}%
                  </span>
                </td>
                <td>
                  <span
                    className={`font-mono font-bold text-[11px] px-2 py-0.5 border border-black ${
                      tx.status === "FLAGGED"
                        ? "bg-[var(--pink)] text-black"
                        : tx.status === "HELD"
                        ? "bg-[var(--orange)] text-black"
                        : tx.status === "REVIEW"
                        ? "bg-[var(--lavender)] text-black"
                        : "bg-[var(--mint)] text-black"
                    }`}
                  >
                    ● {tx.status}
                  </span>
                </td>
                <td>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => onInspect(tx)}
                      className="font-mono text-xs font-bold px-2 py-1 bg-[var(--yellow)] border-[2px] border-black hover:bg-black hover:text-white transition-colors"
                    >
                      INSPECT
                    </button>
                    {tx.status === "FLAGGED" && (
                      <button
                        onClick={() => onShowToast(`🚨 Instant freeze signal dispatched for ${tx.id}`)}
                        className="font-mono text-xs font-bold px-2 py-1 bg-[var(--red)] text-white border-[2px] border-black hover:bg-black transition-colors"
                      >
                        FREEZE
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
