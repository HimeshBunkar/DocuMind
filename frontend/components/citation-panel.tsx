"use client";

import { motion } from "framer-motion";
import { BookOpenText, Clipboard, FileText, ScanSearch } from "lucide-react";
import type { Citation } from "@/lib/schemas";
import { cn } from "@/lib/utils";

type Props = {
  citations: Citation[];
  activeCitation?: Citation | null;
  onSelect: (citation: Citation) => void;
};

export function CitationPanel({ citations, activeCitation, onSelect }: Props) {
  return (
    <aside className="glass-panel flex min-h-0 flex-col rounded-lg">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-md border border-white/10 bg-white/10 text-cyan">
            <ScanSearch className="h-4 w-4" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Sources</h2>
            <p className="text-xs text-white/40">{citations.length} retrieved chunks</p>
          </div>
        </div>
        <button
          type="button"
          title="Copy source text"
          aria-label="Copy source text"
          disabled={!activeCitation && citations.length === 0}
          onClick={() => navigator.clipboard.writeText((activeCitation ?? citations[0])?.text ?? "")}
          className="grid h-8 w-8 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 transition hover:border-cyan/40 hover:text-cyan disabled:opacity-30"
        >
          <Clipboard className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div className="scrollbar-thin min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
        {citations.length ? (
          citations.map((citation, index) => {
            const active =
              activeCitation?.document_id === citation.document_id &&
              activeCitation?.page === citation.page &&
              activeCitation?.paragraph === citation.paragraph;

            return (
              <motion.button
                layout
                key={`${citation.document_id}-${citation.page}-${citation.paragraph}-${index}`}
                type="button"
                onClick={() => onSelect(citation)}
                className={cn(
                  "w-full rounded-lg border p-3 text-left transition",
                  active
                    ? "border-cyan/70 bg-cyan/10 shadow-glow"
                    : "border-white/10 bg-white/[0.045] hover:border-white/20 hover:bg-white/[0.07]"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="flex min-w-0 items-center gap-2 text-xs font-medium text-white/70">
                    <FileText className="h-3.5 w-3.5 shrink-0 text-cyan" aria-hidden="true" />
                    <span className="truncate">{citation.document_name}</span>
                  </span>
                  <span className="rounded-full border border-mint/30 bg-mint/10 px-2 py-0.5 text-xs text-mint">
                    {Math.round(citation.score * 100)}%
                  </span>
                </div>
                <p className="mt-2 text-xs text-white/40">
                  Page {citation.page} · Paragraph {citation.paragraph}
                </p>
                <p className="mt-3 text-sm leading-6 text-white/70">
                  <mark className="rounded bg-cyan/[0.15] px-1 py-0.5 text-white">{citation.text}</mark>
                </p>
              </motion.button>
            );
          })
        ) : (
          <div className="grid min-h-72 place-items-center rounded-lg border border-dashed border-white/10 bg-white/[0.03] p-6 text-center">
            <div>
              <BookOpenText className="mx-auto h-8 w-8 text-white/40" aria-hidden="true" />
              <p className="mt-3 text-sm text-white/50">Citations will appear here.</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
