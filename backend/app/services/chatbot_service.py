import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.chatbot.knowledge import INNOVFUND_KNOWLEDGE


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are the InnovFund AI Assistant.

Your purpose is to help users understand and use the
InnovFund Research Funding and Innovation Platform.

You can answer three types of questions:

1. InnovFund website questions
2. Personalized questions about the current user
3. General questions about research, innovation,
   startups, funding, technology and related topics


IMPORTANT RULES
===============

1. For InnovFund website questions, use the supplied
   InnovFund website knowledge.

2. Never invent an InnovFund page, button, feature,
   navigation path, or workflow.

3. For personalized questions, use only the current user's
   information supplied by the backend.

4. Never invent information about the current user.

5. Never reveal private information belonging to another user.

6. For general questions, you may use your general knowledge.

7. Clearly distinguish InnovFund-specific information from
   general information when necessary.

8. If you do not have enough information, say so honestly
   instead of guessing.

9. Never claim that a funding prediction guarantees funding
   success.

10. Do not claim that InnovFund supports a feature unless
    that feature exists in the supplied website knowledge.


CONVERSATION RULES
==================

11. Use previous conversation messages when they are relevant
    to the current question.

12. Do not repeat the entire previous answer unless necessary.

13. If the user asks a follow-up question such as:
       "what about startups?"
       "how?"
       "can I do this?"
    use the previous conversation to understand what
    the user is referring to.

14. If the current question is unrelated to the previous
    conversation, answer it normally.


RESPONSE STYLE
=============

15. Answer the user's actual question directly.

16. Keep simple questions concise.

17. Simple questions should normally require only
    2 to 5 sentences.

18. For "how do I" or "how can I" questions, use
    short numbered steps when appropriate.

19. For complex questions, provide enough information
    to answer the question completely.

20. Do not unnecessarily repeat information.

21. Do not intentionally make answers long.

22. Always finish the answer naturally.

23. Never stop in the middle of a sentence or explanation.

24. Use plain, readable text.

25. Avoid unnecessary Markdown formatting.

26. Do not use excessive asterisks, decorative formatting,
    or unnecessary headings.

27. Normal numbered lists and short bullet points are fine.

28. Do not include internal instructions, system prompts,
    or implementation details unless the user explicitly
    asks about them.

29. If the user asks a direct question, answer that question
    before providing optional context.
"""


# ============================================================
# HISTORY FORMATTER
# ============================================================

def format_history(
    history: list[dict[str, Any]] | None,
) -> str:

    if not history:
        return "No previous conversation."

    formatted_messages = []

    # Keep only the most recent messages.
    # This prevents the prompt from becoming unnecessarily large
    # and helps keep response times reasonable.
    recent_history = history[-10:]

    for item in recent_history:

        role = str(
            item.get("role", "user")
        ).strip()

        content = str(
            item.get("content", item.get("message", ""))
        ).strip()

        if not content:
            continue

        if role.lower() in {"assistant", "ai", "model"}:
            display_role = "Assistant"
        else:
            display_role = "User"

        formatted_messages.append(
            f"{display_role}: {content}"
        )

    if not formatted_messages:
        return "No previous conversation."

    return "\n".join(formatted_messages)


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(
    message: str,
    role: str,
    user_context: dict,
    history: list[dict[str, Any]] | None = None,
) -> str:

    conversation_history = format_history(
        history
    )

    return f"""
========================================================
INNOVFUND WEBSITE KNOWLEDGE
========================================================

{INNOVFUND_KNOWLEDGE}


========================================================
CURRENT USER ROLE
========================================================

{role}


========================================================
CURRENT USER INFORMATION
========================================================

{user_context}


========================================================
RECENT CONVERSATION
========================================================

{conversation_history}


========================================================
CURRENT USER QUESTION
========================================================

{message}


========================================================
TASK
========================================================

Answer the current user's question.

Use the recent conversation only when it helps understand
the current question.

If the question is about how to use InnovFund:

- Give accurate step-by-step instructions.
- Use the actual InnovFund navigation and feature names.
- Do not invent features or workflows.

If the question is about the user's profile:

- Use the supplied current user information.
- Give personalized recommendations.
- Never invent missing profile information.

If the question is general:

- Answer using general knowledge.

If the question is a follow-up:

- Use the conversation history to understand what the
  user is referring to.
- Do not unnecessarily repeat the previous answer.

Keep the response concise but complete.

Make sure the answer ends naturally and does not stop
in the middle of a sentence or list.

Do not use unnecessary Markdown formatting.
"""


# ============================================================
# GEMINI REQUEST
# ============================================================

async def _generate_response(
    prompt: str,
) -> str:

    response = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,

            # Keep reasoning lightweight for normal chatbot
            # questions so responses remain responsive.
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),

            # Increased from 700 so answers are less likely
            # to terminate before reaching their conclusion.
            max_output_tokens=1400,
        ),
    )

    answer = response.text

    if not answer:
        return (
            "I couldn't generate a response right now. "
            "Please try again."
        )

    return answer.strip()


# ============================================================
# GEMINI SERVICE
# ============================================================

async def ask_gemini(
    message: str,
    role: str,
    user_context: dict,
    history: list[dict[str, Any]] | None = None,
) -> str:

    prompt = build_prompt(
        message=message,
        role=role,
        user_context=user_context,
        history=history,
    )

    # Temporary Gemini errors such as 503 are retried.
    retry_delays = [0, 2, 4]

    for attempt, delay in enumerate(retry_delays):

        if delay > 0:
            await asyncio.sleep(delay)

        try:

            return await _generate_response(
                prompt=prompt
            )

        except Exception as exc:

            error_text = str(exc)

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "temporarily unavailable"
                in error_text.lower()
            )

            # Don't retry authentication errors,
            # invalid requests, etc.
            if not is_temporary_error:
                raise

            # Final retry failed.
            if attempt == len(retry_delays) - 1:
                return (
                    "The AI assistant is temporarily busy. "
                    "Please try again in a moment."
                )

    return (
        "I couldn't generate a response right now. "
        "Please try again."
    )