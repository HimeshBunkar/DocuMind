from __future__ import annotations

from app.models.schemas import Citation


class PromptOrchestrator:
    """Keeps prompt templates and retrieval context formatting in one place."""

    def build_messages(self, question: str, citations: list[Citation], compare: bool) -> list[dict[str, str]]:
        system = (
            "You are DocuMind, a grounded document QA assistant. "
            "Use only the retrieved context. Include page and paragraph references. "
            "Say when the context is insufficient."
        )
        if compare:
            system += " Compare selected documents directly and separate agreements from differences."

        context = "\n\n".join(
            f"[{index}] {citation.document_name} p.{citation.page} para.{citation.paragraph} "
            f"(score {citation.score:.2f}): {citation.text}"
            for index, citation in enumerate(citations, start=1)
        )

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Question: {question}\n\nRetrieved context:\n{context}"}
        ]

    def as_langchain_prompt(self):
        try:
            from langchain_core.prompts import ChatPromptTemplate
        except Exception:
            return None

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are DocuMind. Answer from retrieved context only and cite source page and paragraph."
                ),
                ("human", "Question: {question}\n\nRetrieved context:\n{context}")
            ]
        )
