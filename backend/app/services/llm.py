from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import Citation
from app.services.orchestration import PromptOrchestrator


class ResponseSynthesizer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.prompts = PromptOrchestrator()

    async def answer(self, question: str, citations: list[Citation], compare: bool = False) -> str:
        # Try Gemini first
        if self.settings.llm_provider == "gemini" and self.settings.gemini_api_key:
            try:
                return await self._gemini_answer(question, citations, compare)
            except Exception:
                pass
        # Try OpenAI fallback
        if self.settings.llm_provider == "openai" and self.settings.openai_api_key:
            try:
                return await self._openai_answer(question, citations, compare)
            except Exception:
                pass
        # Local template fallback
        return self._local_answer(question, citations, compare)

    async def _gemini_answer(self, question: str, citations: list[Citation], compare: bool) -> str:
        import asyncio
        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        model = genai.GenerativeModel(self.settings.gemini_chat_model)

        messages = self.prompts.build_messages(question, citations, compare)
        # Gemini uses a single prompt string; combine system + user
        system_text = messages[0]["content"]
        user_text = messages[1]["content"]
        full_prompt = f"{system_text}\n\n{user_text}"

        loop = asyncio.get_event_loop()

        def _call() -> str:
            response = model.generate_content(
                full_prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 1024}
            )
            return response.text

        return await loop.run_in_executor(None, _call)

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
