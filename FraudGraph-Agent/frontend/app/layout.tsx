import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "FRAUDGRAPH // Autonomous Agent Intelligence & Graph Consensus",
  description: "Neo-brutalist autonomous fraud detection platform powered by TigerGraph, multi-agent consensus, and real-time transaction graph reasoning.",
  keywords: ["Neo-Brutalism", "Fintech", "Fraud Detection", "Autonomous Agent", "TigerGraph", "Graph AI"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="paper-texture min-h-screen">
        {children}
      </body>
    </html>
  );
}
