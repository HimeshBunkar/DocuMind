"use client";

import { Database, FileStack, Gauge, Sparkles } from "lucide-react";
import type { DocumentMeta } from "@/lib/schemas";

export function WorkspaceDashboard({ documents }: { documents: DocumentMeta[] }) {
  const readyCount = documents.filter((document) => document.status === "ready").length;
  const chunkCount = documents.reduce((total, document) => total + document.chunk_count, 0);
  const pageCount = documents.reduce((total, document) => total + document.page_count, 0);

  const stats = [
    {
      icon: FileStack,
      label: "Documents",
      value: documents.length.toString()
    },
    {
      icon: Database,
      label: "Chunks",
      value: chunkCount.toLocaleString()
    },
    {
      icon: Gauge,
      label: "Pages",
      value: pageCount.toLocaleString()
    },
    {
      icon: Sparkles,
      label: "Ready",
      value: readyCount.toString()
    }
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className="rounded-lg border border-white/10 bg-white/[0.045] p-4">
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-medium uppercase text-white/40">{stat.label}</span>
              <Icon className="h-4 w-4 text-cyan" aria-hidden="true" />
            </div>
            <p className="mt-3 text-2xl font-semibold text-white">{stat.value}</p>
          </div>
        );
      })}
    </div>
  );
}
