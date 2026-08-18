"""OpenRouter AI service.

Single reusable entry point for every AI feature in the platform.
Replaces the previous Hugging Face Transformers, LangChain, and
OpenAI implementations with one async function:

    generate_ai_response(task: str, content: str) -> str

Add a new task by adding a single entry to ``TASK_PROMPTS`` — no other
code needs to change. Every AI feature (summarization, patent
explanation, concept explanation, literature review, commercialization,
research directions, etc.) routes through this service.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any, Dict

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Task prompts
# ---------------------------------------------------------------------------
# Each entry is the instruction prefix sent to the model. The user's
# content is appended after a "Content" (or equivalent) header so the
# model clearly separates the instruction from the input.

TASK_PROMPTS: Dict[str, str] = {
    "summarize": (
        "Summarize this research paper.\n\n"
        "Include:\n"
        "- Research Problem\n"
        "- Objectives\n"
        "- Methodology\n"
        "- Dataset\n"
        "- Results\n"
        "- Key Contributions\n"
        "- Limitations\n"
        "- Future Work\n\n"
        "Paper\n"
        "{content}"
    ),
    "explain-patent": (
        "Explain this patent in simple language.\n\n"
        "Include:\n"
        "- Problem\n"
        "- Innovation\n"
        "- Novelty\n"
        "- Claims\n"
        "- Applications\n"
        "- Advantages\n"
        "- Limitations\n\n"
        "Patent\n"
        "{content}"
    ),
    "explain-concept": (
        "Explain the following concept for a beginner.\n\n"
        "Include:\n"
        "- Definition\n"
        "- Working Principle\n"
        "- Example\n"
        "- Applications\n"
        "- Advantages\n"
        "- Limitations\n\n"
        "Concept\n"
        "{content}"
    ),
    "literature-review": (
        "Write a structured literature review.\n\n"
        "Identify:\n"
        "- Main Themes\n"
        "- Comparison\n"
        "- Strengths\n"
        "- Weaknesses\n"
        "- Research Gaps\n"
        "- Future Trends\n\n"
        "Content\n"
        "{content}"
    ),
    "commercialization": (
        "Analyze commercialization opportunities.\n\n"
        "Include:\n"
        "- Potential Market\n"
        "- Target Customers\n"
        "- Revenue Model\n"
        "- Competitors\n"
        "- Challenges\n"
        "- Commercial Potential\n\n"
        "Technology\n"
        "{content}"
    ),
    "research-directions": (
        "Suggest future research directions.\n\n"
        "Identify:\n"
        "- Research Gaps\n"
        "- Emerging Trends\n"
        "- Possible Extensions\n"
        "- Novel Ideas\n\n"
        "Content\n"
        "{content}"
    ),
    # ------------------------------------------------------------------
    # Patent Intelligence Dashboard — JSON prompts
    # The model is asked to return STRICT JSON so the frontend can render
    # progress bars, scorecards, and grids without prose parsing.
    # ------------------------------------------------------------------
    "patent-summary": (
        "Explain this patent in concise, well-structured JSON for a researcher.\n\n"
        "Return ONLY valid JSON (no markdown, no commentary) with these keys:\n"
        "{\n"
        '  "simple_explanation": "2-3 sentence plain-language explanation aimed at a non-specialist",\n'
        '  "technical_explanation": "1-2 paragraph technical explanation for a researcher",\n'
        '  "problem": "the problem the patent solves",\n'
        '  "innovation": "what is novel about the approach",\n'
        '  "advantages": ["list", "of", "key", "advantages"],\n'
        '  "limitations": ["list", "of", "limitations"],\n'
        '  "future_improvements": ["list", "of", "future", "improvements"]\n'
        "}\n\n"
        "Patent\n"
        "{content}"
    ),
    "innovation-analysis": (
        "Analyze the innovation potential of this patent and return ONLY valid JSON.\n\n"
        "Score every dimension on a 0-100 scale (integer). Be honest: if the patent is old, "
        "give conservative numbers; if it is novel and high-impact, reflect that.\n\n"
        "Return JSON with these keys:\n"
        "{\n"
        '  "innovation_score": 0-100,\n'
        '  "novelty_score": 0-100,\n'
        '  "commercial_potential": 0-100,\n'
        '  "research_difficulty": 0-100,\n'
        '  "technology_maturity": 0-100,\n'
        '  "future_demand": 0-100,\n'
        '  "investment_potential": 0-100,\n'
        '  "rationale": "1-2 sentence justification"\n'
        "}\n\n"
        "Patent\n"
        "{content}"
    ),
    "tech-gap": (
        "Identify the research gaps that still exist based on this patent. "
        "Return ONLY valid JSON with these keys:\n"
        "{\n"
        '  "missing_features": ["list of features the patent does not address"],\n'
        '  "untapped_opportunities": ["list of opportunities the field has not pursued"],\n'
        '  "possible_improvements": ["list of concrete improvements"],\n'
        '  "future_research_directions": ["list of future research directions"],\n'
        '  "emerging_combinations": ["list of emerging technologies to combine with this one"]\n'
        "}\n\n"
        "Patent\n"
        "{content}"
    ),
    "commercial-applications": (
        "List the most plausible commercial applications of this patent. "
        "Return ONLY valid JSON as an array of objects (at least 6 entries). Use this shape:\n"
        "[\n"
        '  {"industry": "Healthcare", "reason": "1-2 sentence reasoning", "example_use_case": "concrete example"},\n'
        "  ...\n"
        "]\n\n"
        "Cover industries such as Healthcare, Agriculture, Telecommunications, Automotive, "
        "Military, Space, Education, Manufacturing, Energy, Finance, and any other relevant ones.\n\n"
        "Patent\n"
        "{content}"
    ),
    "patent-recommendations": (
        "Act as a senior research advisor. Based on this patent, give the researcher a "
        "decision-ready recommendation. Return ONLY valid JSON with these keys:\n"
        "{\n"
        '  "continue_in_area": "Yes / No / Maybe with one sentence justification",\n'
        '  "improvements": ["list of 2-4 specific things to improve"],\n'
        '  "commercialization_recommended": "Yes / No / Maybe with one sentence justification",\n'
        '  "expected_future_demand": "Low / Medium / High with one sentence justification",\n'
        '  "funding_possibility": "Low / Medium / High with one sentence justification",\n'
        '  "suggested_collaborations": ["list of suggested collaboration profiles"],\n'
        '  "overall_recommendation": "2-3 sentence overall recommendation for the researcher"\n'
        "}\n\n"
        "Patent\n"
        "{content}"
    ),
}

# Legacy aliases — accept the older kebab-case names used elsewhere in
# the codebase so every existing caller still works.
TASK_ALIASES: Dict[str, str] = {
    "explain_patent": "explain-patent",
    "explain_concept": "explain-concept",
    "literature_review": "literature-review",
    "research_directions": "research-directions",
    # New Patent Intelligence Dashboard aliases (snake_case variants).
    "patent_summary": "patent-summary",
    "innovation_analysis": "innovation-analysis",
    "tech_gap": "tech-gap",
    "commercial_applications": "commercial-applications",
    "patent_recommendations": "patent-recommendations",
}


# ---------------------------------------------------------------------------
# Client (cached)
# ---------------------------------------------------------------------------

class OpenRouterConfigError(RuntimeError):
    """Raised when OpenRouter is not configured."""


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    """Return a cached OpenRouter-compatible OpenAI client.

    OpenRouter exposes an OpenAI-compatible API, so the official
    ``openai`` SDK works out of the box when pointed at the
    ``OPENROUTER_BASE_URL``.
    """
    api_key = (settings.OPENROUTER_API_KEY or "").strip()
    if not api_key or api_key == "YOUR_API_KEY":
        raise OpenRouterConfigError(
            "OPENROUTER_API_KEY is not configured. Set it in backend/.env."
        )
    return OpenAI(
        api_key=api_key,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={
            # OpenRouter recommends identifying the app so the key
            # owner can see usage on their dashboard.
            "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
            "X-Title": settings.OPENROUTER_APP_NAME,
        },
    )


def _normalize_task(task: str) -> str:
    """Resolve a task name to a known prompt key."""
    key = (task or "").strip().lower()
    key = TASK_ALIASES.get(key, key)
    if key not in TASK_PROMPTS:
        raise ValueError(
            f"Unknown AI task: {task!r}. "
            f"Supported tasks: {sorted(TASK_PROMPTS)}"
        )
    return key


def _build_prompt(task: str, content: str) -> str:
    template = TASK_PROMPTS[task]
    return template.format(content=(content or "").strip())


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------
# Some dashboard prompts ask the model to return STRICT JSON.  Small models
# often wrap the JSON in ```json ... ``` fences or add a leading sentence,
# so we strip those before parsing.  When parsing fails we return a
# fallback error dict so the route can surface a useful message to the UI
# rather than crashing the dashboard.

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|^\s*```\s*$", re.MULTILINE)


def parse_ai_json(text: str) -> Dict[str, Any]:
    """Best-effort JSON parser for AI responses.

    Strips ````json` fences, locates the first balanced JSON object or
    array in the text, and returns the parsed result. Returns a
    ``{"error": "..."}`` dict on failure so callers can surface a
    graceful error rather than 500-ing.
    """
    if not text:
        return {"error": "empty response from AI"}
    cleaned = _FENCE_RE.sub("", text).strip()
    # Locate the first JSON value (object or array) and try to parse from
    # there.  Models sometimes prepend a one-line intro before the JSON.
    for opener, closer in (("{", "}"), ("[", "]")):
        start = cleaned.find(opener)
        if start == -1:
            continue
        candidate = cleaned[start:]
        # Walk the string keeping track of nesting to find the matching
        # closer.  This is more robust than just looking for the first
        # ``closer`` because the model may include nested objects.
        depth = 0
        in_str = False
        escape = False
        for i, ch in enumerate(candidate):
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    candidate = candidate[: i + 1]
                    break
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try the next matching shape (e.g. array if the model wrapped
            # the object in an extra layer).
            continue
    return {"error": "AI response was not valid JSON", "raw": text[:500]}


# ---------------------------------------------------------------------------
# Public API — the only function callers should use
# ---------------------------------------------------------------------------

async def generate_ai_response(task: str, content: str) -> str:
    """Run an AI task through OpenRouter and return the generated text.

    Parameters
    ----------
    task:
        One of the keys in :data:`TASK_PROMPTS` (e.g. ``"summarize"``).
    content:
        The user-supplied text (paper abstract, patent text, topic, etc.).

    Returns
    -------
    str
        The model's response. Empty string if the model produced nothing.
    """
    normalized = _normalize_task(task)
    if not (content or "").strip():
        raise ValueError("content must not be empty")

    prompt = _build_prompt(normalized, content)
    client = _get_client()
    model = settings.OPENROUTER_MODEL

    logger.info(
        "OpenRouter request: task=%s model=%s content_len=%d",
        normalized,
        model,
        len(content),
    )

    try:
        # The OpenAI SDK is sync, but the call is I/O-bound and
        # FastAPI runs sync endpoints in a threadpool, so this does
        # not block the event loop. Wrap in ``asyncio.to_thread`` for
        # true non-blocking behavior when called from async code.
        import asyncio

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI research assistant. "
                        "Follow the user's instructions precisely and "
                        "respond in clear, well-structured Markdown "
                        "or JSON depending on the user's request."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1500,
        )
    except OpenRouterConfigError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface a clean error to the route
        logger.exception("OpenRouter call failed for task=%s: %s", normalized, exc)
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    if not response.choices:
        logger.warning("OpenRouter returned no choices for task=%s", normalized)
        return ""

    text = (response.choices[0].message.content or "").strip()
    logger.info(
        "OpenRouter response: task=%s response_len=%d",
        normalized,
        len(text),
    )
    return text


def list_supported_tasks() -> list[str]:
    """Return the list of supported task keys."""
    return sorted(TASK_PROMPTS)
