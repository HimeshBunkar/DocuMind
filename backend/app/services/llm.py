from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import Citation
from app.services.orchestration import PromptOrchestrator


class ResponseSynthesizer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.prompts = PromptOrchestrator()

    async def answer(self, question: str, citations: list[Citation], compare: bool = False) -> str:
        if self.settings.llm_provider == "groq" and self.settings.groq_api_key:
            try:
                return await self._groq_answer(question, citations, compare)
            except Exception as e:
                print(f"Groq LLM error: {e}")
        if self.settings.llm_provider == "gemini" and self.settings.gemini_api_key:
            try:
                return await self._gemini_answer(question, citations, compare)
            except Exception as e:
                print(f"Gemini LLM error: {e}")
        if self.settings.llm_provider == "openai" and self.settings.openai_api_key:
            try:
                return await self._openai_answer(question, citations, compare)
            except Exception:
                pass
        return self._local_answer(question, citations, compare)

    async def _groq_answer(self, question: str, citations: list[Citation], compare: bool) -> str:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self.settings.groq_api_key)
        messages = self.prompts.build_messages(question, citations, compare)
        response = await client.chat.completions.create(
            model=self.settings.groq_chat_model,
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )
        return response.choices[0].message.content or ""

    async def _gemini_answer(self, question: str, citations: list[Citation], compare: bool) -> str:
        import asyncio
        from google import genai
        client = genai.Client(api_key=self.settings.gemini_api_key)
        messages = self.prompts.build_messages(question, citations, compare)
        system_text = messages[0]["content"]
        user_text = messages[1]["content"]
        full_prompt = f"{system_text}\n\n{user_text}"
        loop = asyncio.get_event_loop()

        def _call() -> str:
            response = client.models.generate_content(
                model=self.settings.gemini_chat_model,
                contents=full_prompt,
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
            return "\n".join(sections)

        lead = citations[0]
        supporting = citations[1:3]
        answer = (
            f"Based on **{lead.document_name}**: {lead.text} "
            f"(page {lead.page}, paragraph {lead.paragraph})."
        )
        if supporting:
            support_text = " ".join(
                f"Also from {item.document_name}, page {item.page}."
                for item in supporting
            )
            answer = f"{answer}\n\n{support_text}"
        return answer