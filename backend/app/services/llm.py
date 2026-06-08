from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import Citation
from app.services.orchestration import PromptOrchestrator


class ResponseSynthesizer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = settings.llm_provider
        self.prompts = PromptOrchestrator()

    async def answer(self, question: str, citations: list[Citation], compare: bool = False) -> str:
        if self.settings.llm_provider == "openai" and self.settings.openai_api_key:
            try:
                return await self._openai_answer(question, citations, compare)
            except Exception:
                pass
        return self._local_answer(question, citations, compare)

    async def _openai_answer(self, question: str, citations: list[Citation], compare: bool) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        response = await client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=self.prompts.build_messages(question, citations, compare),
            temperature=0.2
        )
        return response.choices[0].message.content or ""

    def _local_answer(self, question: str, citations: list[Citation], compare: bool) -> str:
        if not citations:
            return "I could not find enough grounded context in the uploaded documents to answer that."

        grouped: dict[str, list[Citation]] = {}
        for citation in citations:
            grouped.setdefault(citation.document_name, []).append(citation)

        if compare and len(grouped) > 1:
            sections = ["Here is the grounded comparison I found:"]
            for document_name, items in grouped.items():
                strongest = items[0]
                sections.append(
                    f"- **{document_name}**: {strongest.text} "
                    f"(page {strongest.page}, paragraph {strongest.paragraph})."
                )
            sections.append("The distinction is based on the retrieved passages above, ranked by semantic relevance.")
            return "\n".join(sections)

        lead = citations[0]
        supporting = citations[1:3]
        answer = (
            f"Based on **{lead.document_name}**, the most relevant passage says: "
            f"{lead.text} (page {lead.page}, paragraph {lead.paragraph})."
        )
        if supporting:
            support_text = " ".join(
                f"Additional support appears in {item.document_name}, page {item.page}, paragraph {item.paragraph}."
                for item in supporting
            )
            answer = f"{answer}\n\n{support_text}"
        return answer
