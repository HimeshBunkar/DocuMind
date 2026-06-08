import { CheckCircle2, Clock3, Loader2, XCircle } from "lucide-react";
import type { DocumentMeta } from "@/lib/schemas";
import { cn } from "@/lib/utils";

const statusConfig = {
  queued: {
    icon: Clock3,
    label: "Queued",
    className: "border-amber/30 bg-amber/10 text-amber"
  },
  processing: {
    icon: Loader2,
    label: "Embedding",
    className: "border-cyan/30 bg-cyan/10 text-cyan"
  },
  ready: {
    icon: CheckCircle2,
    label: "Ready",
    className: "border-mint/30 bg-mint/10 text-mint"
  },
  failed: {
    icon: XCircle,
    label: "Failed",
    className: "border-rose/30 bg-rose/10 text-rose"
  }
} satisfies Record<DocumentMeta["status"], { icon: typeof CheckCircle2; label: string; className: string }>;

export function StatusPill({ status }: { status: DocumentMeta["status"] }) {
  const config = statusConfig[status];
  const Icon = config.icon;
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center gap-1.5 rounded-full border px-2.5 text-xs font-medium",
        config.className
      )}
    >
      <Icon className={cn("h-3.5 w-3.5", status === "processing" && "animate-spin")} aria-hidden="true" />
      {config.label}
    </span>
  );
}
