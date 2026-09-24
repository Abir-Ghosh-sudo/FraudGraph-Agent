"use client";

import React, { useEffect } from "react";

interface ToastProps {
  message: string | null;
  onClear: () => void;
}

export function ToastContainer({ message, onClear }: ToastProps) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(() => {
      onClear();
    }, 4000);
    return () => clearTimeout(timer);
  }, [message, onClear]);

  if (!message) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="brutal-toast font-mono text-xs sm:text-sm cursor-pointer"
      onClick={onClear}
    >
      <span className="w-3 h-3 bg-black rounded-none inline-block rotate-45" />
      <span className="text-black font-bold tracking-tight">{message}</span>
      <span className="ml-2 text-black/60 hover:text-black font-black">✕</span>
    </div>
  );
}
