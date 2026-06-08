import type { ChatMessage, Citation, DocumentMeta } from "@/lib/schemas";

export const sampleDocuments: DocumentMeta[] = [
  {
    id: "demo-security-policy",
    name: "Security Review Policy.pdf",
    file_type: "application/pdf",
    status: "ready",
    chunk_count: 128,
    page_count: 18,
    uploaded_at: new Date(Date.now() - 1000 * 60 * 28).toISOString(),
    summary: "Internal security controls, access reviews, and incident response responsibilities."
  },
  {
    id: "demo-vendor-sla",
    name: "Vendor SLA Agreement.pdf",
    file_type: "application/pdf",
    status: "ready",
    chunk_count: 86,
    page_count: 11,
    uploaded_at: new Date(Date.now() - 1000 * 60 * 67).toISOString(),
    summary: "Availability, response windows, support tiers, and service credits."
  }
];

export const sampleCitations: Citation[] = [
  {
    document_id: "demo-security-policy",
    document_name: "Security Review Policy.pdf",
    page: 7,
    paragraph: 4,
    text: "Privileged access must be reviewed every quarter by the system owner and the security operations lead. Exceptions require written approval and must expire within 30 days.",
    score: 0.91
  },
  {
    document_id: "demo-vendor-sla",
    document_name: "Vendor SLA Agreement.pdf",
    page: 5,
    paragraph: 2,
    text: "Priority 1 incidents require acknowledgement within fifteen minutes and continuous remediation updates until the service is restored.",
    score: 0.86
  }
];

export const initialMessages: ChatMessage[] = [
  {
    id: "welcome-assistant",
    role: "assistant",
    createdAt: new Date().toISOString(),
    content:
      "Upload documents, select the files you want in scope, and ask a question. I will ground answers in retrieved passages with page and paragraph citations.",
    citations: sampleCitations
  }
];
