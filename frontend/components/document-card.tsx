"use client";

import { motion } from "framer-motion";
import { FileText, Hash, Layers3, Trash2 } from "lucide-react";
import type { DocumentMeta } from "@/lib/schemas";
import { cn, formatDate, shortId } from "@/lib/utils";
import { StatusPill } from "@/components/status-pill";

type Props = {
  document: DocumentMeta;
  selected: boolean;
  onToggle: () => void;
  onDelete: () => void;
};

export function DocumentCard({ document, selected, onToggle, onDelete }: Props) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "group relative rounded-lg border p-4 transition",
        selected
          ? "border-cyan/60 bg-cyan/10 shadow-glow"
          : "border-white/10 bg-white/[0.045] hover:border-white/20 hover:bg-white/[0.07]"
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        className="absolute inset-0 rounded-lg"
        aria-label={`Select ${document.name}`}
        title={`Select ${document.name}`}
      />
      <div className="relative flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-white/10 bg-white/10 text-cyan">
            <FileText className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-semibold text-white">{document.name}</h3>
            <p className="mt-1 text-xs text-white/50">{formatDate(document.uploaded_at)} · {shortId(document.id)}</p>
          </div>
        </div>
        <button
          type="button"
          title="Delete document"
          aria-label={`Delete ${document.name}`}
          onClick={(event) => {
            event.stopPropagation();
            onDelete();
          }}
          className="relative grid h-8 w-8 shrink-0 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 opacity-0 transition hover:border-rose/40 hover:text-rose group-hover:opacity-100"
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
      <div className="relative mt-4 flex flex-wrap items-center gap-2">
        <StatusPill status={document.status} />
        <span className="inline-flex h-7 items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.06] px-2.5 text-xs text-white/60">
          <Layers3 className="h-3.5 w-3.5" aria-hidden="true" />
          {document.chunk_count} chunks
        </span>
        <span className="inline-flex h-7 items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.06] px-2.5 text-xs text-white/60">
          <Hash className="h-3.5 w-3.5" aria-hidden="true" />
          {document.page_count} pages
        </span>
      </div>
      {document.summary ? (
        <p className="relative mt-3 line-clamp-2 text-xs leading-5 text-white/60">{document.summary}</p>
      ) : null}
    </motion.article>
  );
}
