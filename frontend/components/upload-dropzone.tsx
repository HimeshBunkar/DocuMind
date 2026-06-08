"use client";

import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { FileUp, Loader2, UploadCloud, X } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";

type UploadItem = {
  id: string;
  name: string;
  progress: number;
  status: "uploading" | "done" | "error";
};

type Props = {
  onUpload: (file: File, onProgress: (progress: number) => void) => Promise<void>;
};

export function UploadDropzone({ onUpload }: Props) {
  const [items, setItems] = useState<UploadItem[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        const id = crypto.randomUUID();
        setItems((current) => [
          ...current,
          {
            id,
            name: file.name,
            progress: 0,
            status: "uploading"
          }
        ]);

        onUpload(file, (progress) => {
          setItems((current) =>
            current.map((item) => (item.id === id ? { ...item, progress } : item))
          );
        })
          .then(() => {
            setItems((current) =>
              current.map((item) => (item.id === id ? { ...item, progress: 100, status: "done" } : item))
            );
          })
          .catch(() => {
            setItems((current) =>
              current.map((item) => (item.id === id ? { ...item, status: "error" } : item))
            );
          });
      });
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"]
    }
  });

  return (
    <section className="rounded-lg border border-white/10 bg-white/[0.045] p-3">
      <div
        {...getRootProps()}
        className={cn(
          "flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed px-4 py-6 text-center transition",
          isDragActive
            ? "border-cyan bg-cyan/10 text-white"
            : "border-white/20 bg-black/10 text-white/60 hover:border-cyan/60 hover:bg-cyan/5"
        )}
      >
        <input {...getInputProps()} />
        <div className="grid h-12 w-12 place-items-center rounded-lg border border-white/10 bg-white/10 text-cyan">
          <UploadCloud className="h-6 w-6" aria-hidden="true" />
        </div>
        <p className="mt-3 text-sm font-medium text-white">Drop documents here</p>
        <p className="mt-1 text-xs text-white/50">PDF, DOCX, TXT, MD</p>
      </div>

      <AnimatePresence initial={false}>
        {items.length ? (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 space-y-2 overflow-hidden"
          >
            {items.slice(-3).map((item) => (
              <div key={item.id} className="rounded-md border border-white/10 bg-black/20 p-3">
                <div className="flex items-center justify-between gap-3 text-xs">
                  <span className="flex min-w-0 items-center gap-2 text-white/70">
                    <FileUp className="h-3.5 w-3.5 shrink-0 text-cyan" aria-hidden="true" />
                    <span className="truncate">{item.name}</span>
                  </span>
                  {item.status === "uploading" ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan" aria-hidden="true" />
                  ) : (
                    <button
                      type="button"
                      title="Dismiss"
                      aria-label="Dismiss upload"
                      onClick={() => setItems((current) => current.filter((next) => next.id !== item.id))}
                      className="grid h-6 w-6 place-items-center rounded-md text-white/40 hover:bg-white/10 hover:text-white"
                    >
                      <X className="h-3.5 w-3.5" aria-hidden="true" />
                    </button>
                  )}
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      item.status === "error" ? "bg-rose" : "bg-cyan"
                    )}
                    style={{ width: `${item.status === "error" ? 100 : item.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </section>
  );
}
