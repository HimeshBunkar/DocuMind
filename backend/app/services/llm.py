from __future__ import annotations

from app.core.config import Settings
from app.models.schemas import Citation
from app.services.orchestration import PromptOrchestrator


class ResponseSynthesizer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = settings.llm_provider
        self.prompts = PromptOrchestrator()

    async def answer(
        self,
        question: str,
        citations: list[Citation],
        compare: bool = False
    ) -> str:

        # Gemini
        if (
            self.settings.llm_provider == "gemini"
            and getattr(self.settings, "gemini_api_key", None)
        ):
            try:
                return await self._gemini_answer(
                    question,
                    citations,
                    compare
                )
            except Exception as e:
                print("Gemini Error:", e)

        # OpenAI
        if (
            self.settings.llm_provider == "openai"
            and self.settings.openai_api_key
        ):
            try:
                return await self._openai_answer(
                    question,
                    citations,
                    compare
                )
            except Exception as e:
                print("OpenAI Error:", e)

        return self._local_answer(
            question,
            citations,
            compare
        )

    async def _openai_answer(
        self,
        question: str,
        citations: list[Citation],
        compare: bool
    ) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=self.settings.openai_api_key
        )

        response = await client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=self.prompts.build_messages(
                question,
                citations,
                compare
            ),
            temperature=0.2,
        )

        return response.choices[0].message.content or ""

    async def _gemini_answer(
        self,
        question: str,
        citations: list[Citation],
        compare: bool
    ) -> str:

        from google import genai

        client = genai.Client(
            api_key=self.settings.gemini_api_key
        )

        messages = self.prompts.build_messages(
            question,
            citations,
            compare
        )

        prompt = "\n".join(
            [
                f"{m['role']}: {m['content']}"
                for m in messages
            ]
        )

        response = client.models.generate_content(
    model=self.settings.gemini_chat_model,
    contents=prompt
)

        return response.text

    def _local_answer(
        self,
        question: str,
        citations: list[Citation],
        compare: bool
    ) -> str:

        if not citations:
            return (
                "I could not find enough grounded context "
                "in the uploaded documents to answer that."
            )

        grouped: dict[str, list[Citation]] = {}

        for citation in citations:
            grouped.setdefault(
                citation.document_name,
                []
            ).append(citation)

        if compare and len(grouped) > 1:
            sections = [
                "Here is the grounded comparison I found:"
            ]

            for document_name, items in grouped.items():
                strongest = items[0]

                sections.append(
                    f"- **{document_name}**: "
                    f"{strongest.text} "
                    f"(page {strongest.page}, "
                    f"paragraph {strongest.paragraph})."
                )

            sections.append(
                "The distinction is based on the "
                "retrieved passages above, ranked "
                "by semantic relevance."
            )

            return "\n".join(sections)

        lead = citations[0]
        supporting = citations[1:3]

        answer = (
            f"Based on **{lead.document_name}**, "
            f"the most relevant passage says: "
            f"{lead.text} "
            f"(page {lead.page}, "
            f"paragraph {lead.paragraph})."
        )

        if supporting:
            support_text = " ".join(
                f"Additional support appears in "
                f"{item.document_name}, "
                f"page {item.page}, "
                f"paragraph {item.paragraph}."
                for item in supporting
            )

            answer = (
                f"{answer}\n\n{support_text}"
            )

        return answer