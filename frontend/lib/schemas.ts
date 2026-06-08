import { z } from "zod";

export const documentSchema = z.object({
  id: z.string(),
  name: z.string(),
  file_type: z.string(),
  status: z.enum(["queued", "processing", "ready", "failed"]),
  chunk_count: z.number(),
  page_count: z.number(),
  uploaded_at: z.string(),
  summary: z.string().nullable().optional()
});

export const citationSchema = z.object({
  document_id: z.string(),
  document_name: z.string(),
  page: z.number(),
  paragraph: z.number(),
  text: z.string(),
  score: z.number()
});

export const uploadResponseSchema = z.object({
  document: documentSchema,
  chunks_preview: z.array(citationSchema)
});

export const queryResponseSchema = z.object({
  answer: z.string(),
  citations: z.array(citationSchema),
  latency_ms: z.number(),
  provider: z.string()
});

export const questionSchema = z.object({
  question: z.string().trim().min(2, "Ask a fuller question.").max(2000)
});

export type DocumentMeta = z.infer<typeof documentSchema>;
export type Citation = z.infer<typeof citationSchema>;
export type UploadResponse = z.infer<typeof uploadResponseSchema>;
export type QueryResponse = z.infer<typeof queryResponseSchema>;

export type QueryMode = "single" | "compare";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  citations?: Citation[];
  pending?: boolean;
};
