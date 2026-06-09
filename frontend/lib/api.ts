import {
  citationSchema,
  documentSchema,
  queryResponseSchema,
  type Citation,
  type DocumentMeta,
  type QueryMode,
  type QueryResponse,
  type UploadResponse,
  uploadResponseSchema
} from "@/lib/schemas";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export async function fetchDocuments(): Promise<DocumentMeta[]> {
  const response = await fetch(`${API_URL}/documents`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load documents.");
  }
  const payload = await response.json();
  return documentSchema.array().parse(payload);
}

export function uploadDocument(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/documents/upload`);

    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable) {
        return;
      }
      onProgress?.(Math.round((event.loaded / event.total) * 100));
    };

    xhr.onload = () => {
      if (xhr.status < 200 || xhr.status >= 300) {
        reject(new Error(xhr.responseText || "Upload failed."));
        return;
      }
      try {
        resolve(uploadResponseSchema.parse(JSON.parse(xhr.responseText)));
      } catch (error) {
        reject(error);
      }
    };

    xhr.onerror = () => reject(new Error("Upload failed."));
    xhr.send(form);
  });
}

export async function deleteDocument(documentId: string) {
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error("Unable to delete document.");
  }
  return response.json();
}

export async function queryDocuments(params: {
  question: string;
  documentIds: string[];
  mode: QueryMode;
}): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question: params.question,
      document_ids: params.documentIds,
      mode: params.mode,
      top_k: params.mode === "compare" ? 8 : 5
    })
  });
  if (!response.ok) {
    throw new Error("Query failed.");
  }
  return queryResponseSchema.parse(await response.json());
}

export async function streamQuery(
  params: {
    question: string;
    documentIds: string[];
    mode: QueryMode;
  },
  handlers: {
    onToken: (token: string) => void;
    onCitations: (citations: Citation[]) => void;
  }
) {
  const response = await fetch(`${API_URL}/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question: params.question,
      document_ids: params.documentIds,
      mode: params.mode,
      top_k: params.mode === "compare" ? 8 : 5
    })
  });

  if (!response.ok || !response.body) {
    const fallback = await queryDocuments(params);
    handlers.onCitations(fallback.citations);
    handlers.onToken(fallback.answer);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const packets = buffer.split("\n\n");
    buffer = packets.pop() ?? "";

    for (const packet of packets) {
      const dataLine = packet
        .split("\n")
        .map((line) => line.trim())
        .find((line) => line.startsWith("data:"));
      if (!dataLine) {
        continue;
      }
      const event = JSON.parse(dataLine.replace(/^data:\s*/, ""));
      if (event.type === "token" && typeof event.value === "string") {
        handlers.onToken(event.value);
      }
      if (event.type === "citations" && Array.isArray(event.value)) {
        handlers.onCitations(citationSchema.array().parse(event.value));
      }
      if (event.type === "error") {
        throw new Error(String(event.value));
      }
    }
  }
}
