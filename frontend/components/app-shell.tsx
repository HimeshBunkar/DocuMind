"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { BrainCircuit, Menu, PanelLeftClose, RefreshCw, SearchCheck, ServerCrash, ShieldCheck } from "lucide-react";
import { ChatPanel } from "@/components/chat-panel";
import { CitationPanel } from "@/components/citation-panel";
import { DocumentCard } from "@/components/document-card";
import { UploadDropzone } from "@/components/upload-dropzone";
import { WorkspaceDashboard } from "@/components/workspace-dashboard";
import { deleteDocument, fetchDocuments, streamQuery, uploadDocument } from "@/lib/api";
import { initialMessages, sampleCitations, sampleDocuments } from "@/lib/mock-data";
import type { ChatMessage, Citation, DocumentMeta, QueryMode } from "@/lib/schemas";
import { cn } from "@/lib/utils";

export function AppShell() {
  const queryClient = useQueryClient();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState<QueryMode>("single");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [currentCitations, setCurrentCitations] = useState<Citation[]>(sampleCitations);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(sampleCitations[0]);
  const [isStreaming, setIsStreaming] = useState(false);

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments
  });

  const apiOffline = documentsQuery.isError;
  const documents = useMemo<DocumentMeta[]>(() => {
    if (apiOffline) {
      return sampleDocuments;
    }
    return documentsQuery.data ?? [];
  }, [apiOffline, documentsQuery.data]);

  const readyDocumentIds = useMemo(
    () => documents.filter((document) => document.status === "ready").map((document) => document.id),
    [documents]
  );

  useEffect(() => {
    setSelectedIds((current) => {
      const stillValid = current.filter((id) => readyDocumentIds.includes(id));
      if (stillValid.length) {
        return stillValid;
      }
      return readyDocumentIds;
    });
  }, [readyDocumentIds]);

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] })
  });

  const selectedCount = selectedIds.length || readyDocumentIds.length;

  async function handleUpload(file: File, onProgress: (progress: number) => void) {
    if (apiOffline) {
      onProgress(100);
      await new Promise((resolve) => setTimeout(resolve, 500));
      return;
    }
    await uploadDocument(file, onProgress);
    await queryClient.invalidateQueries({ queryKey: ["documents"] });
  }

  function toggleDocument(documentId: string) {
    setSelectedIds((current) =>
      current.includes(documentId)
        ? current.filter((id) => id !== documentId)
        : [...current, documentId]
    );
  }

  async function handleQuestion(question: string) {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      createdAt: new Date().toISOString()
    };
    const assistantId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      pending: true,
      citations: []
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setIsStreaming(true);

    if (apiOffline) {
      await runDemoStream(question, assistantId, mode);
      setIsStreaming(false);
      return;
    }

    try {
      await streamQuery(
        {
          question,
          documentIds: selectedIds.length ? selectedIds : readyDocumentIds,
          mode
        },
        {
          onToken: (token) => {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId
                  ? { ...message, content: `${message.content}${token}`, pending: false }
                  : message
              )
            );
          },
          onCitations: (citations) => {
            setCurrentCitations(citations);
            setActiveCitation(citations[0] ?? null);
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId ? { ...message, citations } : message
              )
            );
          }
        }
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "The query could not be completed.";
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content: `I could not reach the retrieval service. ${message}`,
                pending: false
              }
            : item
        )
      );
    } finally {
      setMessages((current) =>
        current.map((message) => (message.id === assistantId ? { ...message, pending: false } : message))
      );
      setIsStreaming(false);
    }
  }

  async function runDemoStream(question: string, assistantId: string, currentMode: QueryMode) {
    const answer =
      currentMode === "compare"
        ? "Here is the grounded comparison I found:\n\n- **Security Review Policy.pdf** requires quarterly privileged-access reviews with written, time-limited exceptions.\n- **Vendor SLA Agreement.pdf** focuses on operational response commitments, especially fifteen-minute acknowledgement for priority incidents.\n\nTogether, the documents separate internal governance from vendor response obligations."
        : `The strongest retrieved passage for "${question}" says privileged access should be reviewed quarterly and exceptions must expire within 30 days. The supporting SLA passage adds that priority incidents require rapid acknowledgement and continuous remediation updates.`;

    setCurrentCitations(sampleCitations);
    setActiveCitation(sampleCitations[0]);
    setMessages((current) =>
      current.map((message) =>
        message.id === assistantId ? { ...message, citations: sampleCitations } : message
      )
    );

    for (const token of answer.split(" ")) {
      await new Promise((resolve) => setTimeout(resolve, 24));
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, content: `${message.content}${token} `, pending: false }
            : message
        )
      );
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-mesh p-3 text-white md:p-4">
      <div className="pointer-events-none absolute inset-0 opacity-[0.55] [background-image:linear-gradient(rgba(255,255,255,0.055)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.045)_1px,transparent_1px)] [background-size:42px_42px]" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-cyan/10 to-transparent" />

      <div className="relative mx-auto flex h-[calc(100vh-1.5rem)] max-w-[1500px] gap-3 md:h-[calc(100vh-2rem)] md:gap-4">
        <AnimatePresence initial={false}>
          {sidebarOpen ? (
            <motion.aside
              initial={{ x: -28, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -28, opacity: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 28 }}
              className="glass-panel fixed inset-y-3 left-3 z-30 flex w-[min(90vw,380px)] flex-col rounded-lg md:static md:inset-auto md:w-[370px]"
            >
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                <div className="flex min-w-0 items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center overflow-hidden rounded-lg border border-cyan/25 bg-cyan/10">
                    <img src="/documind-signal.png" alt="" className="h-full w-full object-cover" />
                  </div>
                  <div className="min-w-0">
                    <h1 className="truncate text-base font-semibold text-white">DocuMind</h1>
                    <p className="text-xs text-white/50">RAG workspace</p>
                  </div>
                </div>
                <button
                  type="button"
                  title="Collapse sidebar"
                  aria-label="Collapse sidebar"
                  onClick={() => setSidebarOpen(false)}
                  className="grid h-9 w-9 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 transition hover:border-cyan/40 hover:text-cyan"
                >
                  <PanelLeftClose className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>

              <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
                <UploadDropzone onUpload={handleUpload} />

                <div className="mt-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-semibold text-white">Library</h2>
                    <p className="text-xs text-white/50">{documents.length} indexed files</p>
                  </div>
                  <button
                    type="button"
                    title="Refresh documents"
                    aria-label="Refresh documents"
                    onClick={() => queryClient.invalidateQueries({ queryKey: ["documents"] })}
                    className="grid h-8 w-8 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 transition hover:border-cyan/40 hover:text-cyan"
                  >
                    <RefreshCw className={cn("h-4 w-4", documentsQuery.isFetching && "animate-spin")} aria-hidden="true" />
                  </button>
                </div>

                {apiOffline ? (
                  <div className="mt-3 flex items-center gap-2 rounded-lg border border-amber/25 bg-amber/10 px-3 py-2 text-xs text-amber">
                    <ServerCrash className="h-4 w-4 shrink-0" aria-hidden="true" />
                    Backend offline; showing demo workspace.
                  </div>
                ) : null}

                <div className="mt-3 space-y-3">
                  {documents.length ? (
                    documents.map((document) => (
                      <DocumentCard
                        key={document.id}
                        document={document}
                        selected={selectedIds.includes(document.id) || (!selectedIds.length && readyDocumentIds.includes(document.id))}
                        onToggle={() => toggleDocument(document.id)}
                        onDelete={() => {
                          if (!apiOffline) {
                            deleteMutation.mutate(document.id);
                          }
                        }}
                      />
                    ))
                  ) : (
                    <div className="rounded-lg border border-dashed border-white/10 bg-white/[0.03] p-6 text-center">
                      <SearchCheck className="mx-auto h-8 w-8 text-white/40" aria-hidden="true" />
                      <p className="mt-3 text-sm text-white/60">No documents indexed yet.</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.aside>
          ) : null}
        </AnimatePresence>

        <div className="flex min-w-0 flex-1 flex-col gap-3 md:gap-4">
          <header className="glass-panel flex min-h-16 items-center justify-between rounded-lg px-4">
            <div className="flex min-w-0 items-center gap-3">
              {!sidebarOpen ? (
                <button
                  type="button"
                  title="Open sidebar"
                  aria-label="Open sidebar"
                  onClick={() => setSidebarOpen(true)}
                  className="grid h-9 w-9 shrink-0 place-items-center rounded-md border border-white/10 bg-white/[0.06] text-white/60 transition hover:border-cyan/40 hover:text-cyan"
                >
                  <Menu className="h-4 w-4" aria-hidden="true" />
                </button>
              ) : null}
              <div className="min-w-0">
                <p className="text-xs text-white/50">AI document intelligence</p>
                <h2 className="truncate text-lg font-semibold text-white">Grounded answers with paragraph citations</h2>
              </div>
            </div>
            <div className="hidden items-center gap-2 md:flex">
              <span className="inline-flex h-8 items-center gap-1.5 rounded-full border border-mint/25 bg-mint/10 px-3 text-xs text-mint">
                <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
                Citation-first
              </span>
              <span className="inline-flex h-8 items-center gap-1.5 rounded-full border border-cyan/25 bg-cyan/10 px-3 text-xs text-cyan">
                <BrainCircuit className="h-3.5 w-3.5" aria-hidden="true" />
                {mode === "compare" ? "Comparison" : "Retrieval"}
              </span>
            </div>
          </header>

          <WorkspaceDashboard documents={documents} />

          <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1fr)_410px]">
            <ChatPanel
              messages={messages}
              mode={mode}
              selectedCount={selectedCount}
              isStreaming={isStreaming}
              onModeChange={setMode}
              onSubmit={handleQuestion}
              onCitationSelect={(citation) => {
                setActiveCitation(citation);
                setCurrentCitations((current) => {
                  const exists = current.some(
                    (item) =>
                      item.document_id === citation.document_id &&
                      item.page === citation.page &&
                      item.paragraph === citation.paragraph
                  );
                  return exists ? current : [citation, ...current];
                });
              }}
            />
            <CitationPanel
              citations={currentCitations}
              activeCitation={activeCitation}
              onSelect={setActiveCitation}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
