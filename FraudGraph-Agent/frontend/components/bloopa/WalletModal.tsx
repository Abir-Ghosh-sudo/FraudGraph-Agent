"use client";

import React, { useState } from "react";

interface WalletModalProps {
  isOpen: boolean;
  onClose: () => void;
  walletConnected: boolean;
  walletAddress: string | null;
  algoBalance: number;
  onConnect: (address: string) => void;
  onDisconnect: () => void;
}

export function WalletModal({
  isOpen,
  onClose,
  walletConnected,
  walletAddress,
  algoBalance,
  onConnect,
  onDisconnect,
}: WalletModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const mockWallets = [
    { name: "TigerGraph Agent Key", icon: "🐅", desc: "Automated GSQL cognitive agent" },
    { name: "Fintech Compliance Signer", icon: "🏛️", desc: "Corporate multi-sig approval wallet" },
    { name: "Pera / Algorand Signer", icon: "🟡", desc: "Decentralized on-chain identity" },
    { name: "Defly Agent Vault", icon: "🟣", desc: "Autonomous liquidity safeguard" },
  ];

  const handleCopy = () => {
    if (walletAddress) {
      navigator.clipboard.writeText(walletAddress);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/65 backdrop-blur-xs select-none">
      <div className="relative w-full max-w-md bg-[#f7f4ea] border-[4px] border-black p-6 sm:p-7 shadow-[10px_10px_0_#050505]">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 w-9 h-9 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base flex items-center justify-center shadow-[2px_2px_0_#050505] cursor-pointer"
        >
          ✕
        </button>

        <div className="mb-6">
          <span className="sticker sticker-mint text-xs font-mono font-bold mb-2">
            AGENT AUTHENTICATION
          </span>
          <h3 className="font-syne font-black text-2xl sm:text-3xl text-black uppercase tracking-tight mt-1">
            {walletConnected ? "Active Agent Key" : "Connect Signer"}
          </h3>
          <p className="font-mono text-xs font-semibold text-neutral-600 mt-1">
            {walletConnected
              ? "Your autonomous agent is authenticated to dispatch enforcement actions."
              : "Select an agent signer or compliance identity to proceed."}
          </p>
        </div>

        {walletConnected && walletAddress ? (
          <div className="space-y-4">
            <div className="bg-white border-[3px] border-black p-4 shadow-[3px_3px_0_#050505]">
              <div className="flex items-center justify-between text-xs font-mono font-bold text-neutral-500 mb-1">
                <span>AGENT ID</span>
                <span className="text-[#16a34a] font-black">● LIVE</span>
              </div>
              <div className="font-mono font-bold text-xs sm:text-sm text-black break-all bg-neutral-50 p-2 border border-neutral-300">
                {walletAddress}
              </div>
              <div className="mt-3 flex items-center justify-between">
                <button
                  type="button"
                  onClick={handleCopy}
                  className="text-xs font-mono font-bold text-neutral-700 hover:text-black underline"
                >
                  {copied ? "✓ Copied!" : "Copy ID"}
                </button>
                <div className="text-right">
                  <span className="font-mono text-xs text-neutral-500 block">Stake:</span>
                  <span className="font-syne font-black text-lg text-black">
                    {algoBalance.toFixed(2)} ALGO
                  </span>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                onDisconnect();
                onClose();
              }}
              className="w-full bg-[#ff91b8] hover:bg-[#ff7ba8] active:translate-x-[2px] active:translate-y-[2px] border-[3px] border-black py-3 font-syne font-black uppercase text-sm tracking-wider shadow-[4px_4px_0_#050505] cursor-pointer"
            >
              DISCONNECT SIGNER
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {mockWallets.map((w, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  const dummyAddr = `AGENT-${Math.random().toString(36).substring(2, 8).toUpperCase()}-7X`;
                  onConnect(dummyAddr);
                  onClose();
                }}
                className="w-full bg-white hover:bg-[#fffde6] active:translate-x-[2px] active:translate-y-[2px] border-[2.5px] border-black p-3.5 shadow-[3px_3px_0_#050505] flex items-center justify-between group transition-all text-left cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{w.icon}</span>
                  <div>
                    <div className="font-syne font-bold text-sm text-black">
                      {w.name}
                    </div>
                    <div className="font-mono text-[11px] text-neutral-500 font-semibold">
                      {w.desc}
                    </div>
                  </div>
                </div>
                <span className="font-mono font-black text-sm text-black">→</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
