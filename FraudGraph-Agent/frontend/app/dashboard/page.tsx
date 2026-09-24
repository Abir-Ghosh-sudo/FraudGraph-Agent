"use client";

import { redirect } from "next/navigation";
import { useEffect } from "react";

export default function DashboardPage() {
  useEffect(() => {
    window.location.href = "/";
  }, []);

  return null;
}
