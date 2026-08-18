from __future__ import annotations

import asyncio
from typing import List

from app.core.logging import logger
from app.services.ai_service import generate_ai_response


class ResearchAssistant:
    """Thin compatibility wrapper around the OpenRouter AI service."""

    async def summarize(
        self, text: str, max_length: int = 200, min_length: int = 60
    ) -> str:
        return await generate_ai_response(task="summarize", content=text)

    async def explain_patent(self, patent_text: str) -> str:
        return await generate_ai_response(task="explain-patent", content=patent_text)

    async def explain_concept(self, concept: str) -> str:
        return await generate_ai_response(task="explain-concept", content=concept)

    async def generate_literature_review(self, topic: str) -> str:
        return await generate_ai_response(task="literature-review", content=topic)

    async def commercialization_opportunities(self, abstract: str) -> List[str]:
        text = await generate_ai_response(task="commercialization", content=abstract)
        return _to_list(text)

    async def suggest_research_directions(self, abstract: str) -> List[str]:
        text = await generate_ai_response(task="research-directions", content=abstract)
        return _to_list(text)


def _to_list(text: str) -> List[str]:
    """Convert a free-form model response into a list of bullet points.

    Falls back to a single-item list if the response has no obvious
    list structure, so the legacy ``[str]`` contract is preserved.
    """
    if not text:
        return []
    lines = [ln.strip(" -\t•*") for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if len(ln) > 3]
    return lines or [text]


research_assistant = ResearchAssistant()
