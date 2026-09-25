"use client";

import React, { useEffect, useCallback } from "react";
import { FraudGraphCanvas } from "@/components/brutalist/FraudGraphCanvas";

interface GraphExplorerModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTarget?: string;
  initialTargetType?: "customer" | "transaction" | "card" | "account";
  onShowToast?: (msg: string) => void;
}

export function GraphExplorerModal({
  isOpen,
  onClose,
  initialTarget = "C12382",
  initialTargetType = "customer",
  onShowToast,
}: GraphExplorerModalProps) {
  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (!isOpen) return;

    // Body scroll lock
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="TigerGraph Topology Explorer Modal"
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-xs select-none animate-[fade-in_0.15s_ease-out]"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-[min(1180px,calc(100vw-24px))] max-h-[calc(100vh-28px)] bg-[#f7f4ea] border-[4px] border-black p-4 sm:p-6 shadow-[14px_14px_0_#050505] overflow-y-auto"
      >
        {/* Physical Paper Tape Accents */}
        <div className="tape-strip" />
        <div className="tape-strip tape-strip-right" />

        {/* Modal Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Graph Explorer"
          className="absolute top-3 right-3 sm:top-4 sm:right-4 w-9 h-9 sm:w-10 sm:h-10 bg-white hover:bg-neutral-100 active:translate-x-[1px] active:translate-y-[1px] border-[2.5px] border-black font-mono font-black text-base sm:text-lg flex items-center justify-center shadow-[3px_3px_0_#050505] cursor-pointer z-40 transition-transform"
        >
          ✕
        </button>

        {/* Graph Content */}
        <div className="mt-2">
          <FraudGraphCanvas
            initialTarget={initialTarget}
            initialTargetType={initialTargetType}
            onAction={(msg) => onShowToast?.(msg)}
          />
        </div>
      </div>
    </div>
  );
}

export default GraphExplorerModal;
