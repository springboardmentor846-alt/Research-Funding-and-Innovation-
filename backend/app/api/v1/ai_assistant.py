"""AI Assistant endpoints.

Every AI feature on the platform is funnelled through the single
``app.services.ai_service.generate_ai_response`` function, which calls
OpenRouter. This module is the HTTP layer — it accepts a request,
delegates to the service, and shapes the response.

Two surfaces are exposed:

1. ``POST /ai-assistant`` — the unified endpoint requested by the
   platform team. Body: ``{task, content}`` → ``{success, response}``.
2. ``POST /ai/{task}`` — the original per-task endpoints (kept so
   legacy callers and the patents ``/explain`` route keep working).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.deps import get_current_user
from app.core.logging import logger
from app.models.user import User
from app.services.ai_service import (
    generate_ai_response,
    list_supported_tasks,
    OpenRouterConfigError,
)


# Unified endpoint lives at the top level (no prefix) so the
# mounted path is exactly ``/api/v1/ai-assistant``.
unified_router = APIRouter(tags=["AI Assistant"])


# Legacy per-task endpoints live under ``/ai/*``.
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AIAssistantRequest(BaseModel):
    """Unified AI Assistant request body."""
    task: str = Field(
        ...,
        description="AI task identifier, e.g. 'summarize', 'explain-patent'.",
    )
    content: str = Field(
        ...,
        description="Text to process (paper, patent, topic, abstract, ...).",
    )


class AIAssistantResponse(BaseModel):
    success: bool = True
    response: str = ""


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 200
    min_length: int = 60


class ExplainConceptRequest(BaseModel):
    concept: str


class LiteratureReviewRequest(BaseModel):
    topic: str


class CommercialRequest(BaseModel):
    abstract: str


class ResearchDirectionsRequest(BaseModel):
    abstract: str


class ExplainPatentRequest(BaseModel):
    text: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _run_task(task: str, content: str) -> str:
    """Run a single AI task, translating domain errors into HTTP errors."""
    try:
        return await generate_ai_response(task=task, content=content)
    except OpenRouterConfigError as exc:
        logger.error("OpenRouter not configured: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        # ``generate_ai_response`` re-raises SDK failures as
        # ``RuntimeError(message)`` where the message starts with a
        # short tag like "openai.AuthenticationError" or
        # "openai.RateLimitError". Surface those to the caller so the
        # user can act (rotate key, retry later, etc.) instead of
        # seeing only a generic 502.
        msg = str(exc)
        lowered = msg.lower()
        logger.error("AI task '%s' failed: %s", task, exc)
        if "authenticationerror" in lowered or "user not found" in lowered:
            raise HTTPException(
                status_code=503,
                detail=(
                    "OpenRouter authentication failed. "
                    "Check OPENROUTER_API_KEY in backend/.env."
                ),
            )
        if "rate" in lowered and "limit" in lowered:
            raise HTTPException(
                status_code=503,
                detail=(
                    "OpenRouter rate limit reached. Please try again in a moment."
                ),
            )
        raise HTTPException(
            status_code=502,
            detail="Unable to generate AI response. Please try again.",
        )


# ---------------------------------------------------------------------------
# Unified endpoint (POST /ai-assistant)
# ---------------------------------------------------------------------------

@unified_router.post(
    "/ai-assistant",
    response_model=AIAssistantResponse,
    summary="Unified AI Assistant endpoint",
)
async def ai_assistant(
    req: AIAssistantRequest,
    _current: User = Depends(get_current_user),
):
    """Run an AI task and return the generated text.

    Body:
        ``{"task": "summarize", "content": "..."}``

    Response:
        ``{"success": true, "response": "..."}``
    """
    response_text = await _run_task(req.task, req.content)
    return AIAssistantResponse(success=True, response=response_text)


# ---------------------------------------------------------------------------
# Legacy per-task endpoints — preserved for backward compatibility
# ---------------------------------------------------------------------------

@router.post("/summarize")
async def summarize(
    req: SummarizeRequest,
    _current: User = Depends(get_current_user),
):
    text = await _run_task("summarize", req.text)
    return {"summary": text}


@router.post("/explain-patent")
async def explain_patent(
    req: ExplainPatentRequest,
    _current: User = Depends(get_current_user),
):
    if len(req.text) < 50:
        raise HTTPException(status_code=400, detail="Patent text too short")
    text = await _run_task("explain-patent", req.text)
    return {"explanation": text}


@router.post("/explain-concept")
async def explain_concept(
    req: ExplainConceptRequest,
    _current: User = Depends(get_current_user),
):
    text = await _run_task("explain-concept", req.concept)
    return {"explanation": text}


@router.post("/literature-review")
async def literature_review(
    req: LiteratureReviewRequest,
    _current: User = Depends(get_current_user),
):
    text = await _run_task("literature-review", req.topic)
    return {"review": text}


@router.post("/commercialization")
async def commercialization(
    req: CommercialRequest,
    _current: User = Depends(get_current_user),
):
    text = await _run_task("commercialization", req.abstract)
    return {"opportunities": text}


@router.post("/research-directions")
async def research_directions(
    req: ResearchDirectionsRequest,
    _current: User = Depends(get_current_user),
):
    text = await _run_task("research-directions", req.abstract)
    return {"directions": text}


@router.get("/tasks", summary="List supported AI tasks")
async def get_supported_tasks(_current: User = Depends(get_current_user)):
    return {"tasks": list_supported_tasks()}
