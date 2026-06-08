"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Bot, Clipboard, CornerDownLeft, Loader2, MessageSquareText, Scale, Send, UserRound } from "lucide-react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import type { ChatMessage, Citation, QueryMode } from "@/lib/schemas";
import { questionSchema } from "@/lib/schemas";
import { cn } from "@/lib/utils";

type Props = {
  messages: ChatMessage[];
  mode: QueryMode;
  selectedCount: number;
  isStreaming: boolean;
  onModeChange: (mode: QueryMode) => void;
  onSubmit: (question: string) => Promise<void>;
  onCitationSelect: (citation: Citation) => void;
};

export function ChatPanel({
  messages,
  mode,
  selectedCount,
  isStreaming,
  onModeChange,
  onSubmit,
  onCitationSelect
}: Props) {
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    viewportRef.current?.scrollTo({
      top: viewportRef.current.scrollHeight,
      behavior: "smooth"
    });
  }, [messages]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const parsed = questionSchema.safeParse({ question });
    if (!parsed.success) {
      setError(parsed.error.errors[0]?.message ?? "Question is invalid.");
      return;
    }
    setError(null);
    setQuestion("");
    await onSubmit(parsed.data.question);
  }

  return (
    <section className="glass-panel flex min-h-0 flex-col rounded-lg">
      <div className="flex flex-col gap-3 border-b border-white/10 px-4 py-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-md border border-white/10 bg-white/10 text-cyan">
            <MessageSquareText className="h-4 w-4" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Ask DocuMind</h2>
            <p className="text-xs text-white/40">{selectedCount} documents in scope</p>
          </div>
        </div>
        <div className="inline-grid grid-cols-2 rounded-lg border border-white/10 bg-black/20 p-1">
          <button
            type="button"
            onClick={() => onModeChange("single")}
            className={cn(
              "h-8 rounded-md px-3 text-xs font-medium transition",
              mode === "single" ? "bg-white/[0.14] text-white" : "text-white/50 hover:text-white"
            )}
          >
            Chat
          </button>
          <button
            type="button"
            onClick={() => onModeChange("compare")}
            className={cn(
              "flex h-8 items-center justify-center gap-1.5 rounded-md px-3 text-xs font-medium transition",
              mode === "compare" ? "bg-white/[0.14] text-white" : "text-white/50 hover:text-white"
            )}
          >
            <Scale className="h-3.5 w-3.5" aria-hidden="true" />
            Compare
          </button>
        </div>
      </div>

      <div ref={viewportRef} className="scrollbar-thin min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className={cn("flex gap-3", message.role === "user" && "justify-end")}
            >
              {message.role === "assistant" ? (
                <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-md border border-cyan/25 bg-cyan/10 text-cyan">
                  <Bot className="h-4 w-4" aria-hidden="true" />
                </div>
              ) : null}
              <div
                className={cn(
                  "max-w-[86%] rounded-lg border px-4 py-3",
                  message.role === "assistant"
                    ? "border-white/10 bg-white/[0.055]"
                    : "border-cyan/40 bg-cyan/10"
                )}
              >
                <div className="markdown-body text-sm leading-6 text-white/80">
                  {message.pending && !message.content ? (
                    <span className="inline-flex items-center gap-2 text-white/50">
                      <Loader2 className="h-4 w-4 animate-spin text-cyan" aria-hidden="true" />
                      Thinking
                    </span>
                  ) : (
                    <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{message.content}</ReactMarkdown>
                  )}
                </div>
                {message.citations?.length ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.citations.slice(0, 4).map((citation, index) => (
                      <button
                        key={`${citation.document_id}-${citation.page}-${citation.paragraph}-${index}`}
                        type="button"
                        onClick={() => onCitationSelect(citation)}
                        className="rounded-full border border-white/10 bg-black/20 px-2.5 py-1 text-xs text-white/60 transition hover:border-cyan/40 hover:text-cyan"
                      >
                        p.{citation.page} ¶{citation.paragraph}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
              {message.role === "user" ? (
                <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-md border border-white/10 bg-white/10 text-white/70">
                  <UserRound className="h-4 w-4" aria-hidden="true" />
                </div>
              ) : null}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <form onSubmit={handleSubmit} className="border-t border-white/10 p-3">
        <div className="rounded-lg border border-white/10 bg-black/25 p-2">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            rows={3}
            placeholder={mode === "compare" ? "Compare the selected documents on..." : "Ask a grounded question..."}
            className="min-h-20 w-full resize-none border-0 bg-transparent px-2 py-2 text-sm leading-6 text-white outline-none placeholder:text-white/40"
          />
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs text-white/40">
              <CornerDownLeft className="h-3.5 w-3.5" aria-hidden="true" />
              Enter
              {error ? <span className="text-rose">{error}</span> : null}
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                title="Copy last response"
                aria-label="Copy last response"
                onClick={() => {
                  const last = [...messages].reverse().find((message) => message.role === "assistant");
                  navigator.clipboard.writeText(last?.content ?? "");
                }}
                className="grid h-9 w-9 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 transition hover:border-cyan/40 hover:text-cyan"
              >
                <Clipboard className="h-4 w-4" aria-hidden="true" />
              </button>
              <button
                type="submit"
                disabled={isStreaming}
                title="Send"
                aria-label="Send"
                className="grid h-9 w-9 place-items-center rounded-md border border-cyan/40 bg-cyan text-ink transition hover:bg-mint disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isStreaming ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Send className="h-4 w-4" aria-hidden="true" />}
              </button>
            </div>
          </div>
        </div>
      </form>
    </section>
  );
}
