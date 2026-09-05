"""
AI Assistant chatbot service, powered by Google Gemini.

Requires a GEMINI_API_KEY (free tier available at
https://aistudio.google.com/apikey). The Gemini client is created lazily —
on the first actual chat request — rather than at import time, so a
missing/invalid key never crashes the whole application at startup. It
only surfaces as a clear error the moment someone tries to use the chatbot.
"""
import asyncio
import os
from typing import Any

from dotenv import load_dotenv

from app.chatbot.knowledge import PLATFORM_KNOWLEDGE

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_client = None


class ChatbotNotConfiguredError(Exception):
    """Raised when the chatbot is used but no GEMINI_API_KEY is set."""


def _get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ChatbotNotConfiguredError(
                "GEMINI_API_KEY is not configured. Get a free key at "
                "https://aistudio.google.com/apikey and add it to your .env file."
            )
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


SYSTEM_INSTRUCTION = """
You are the AI Assistant for the Research Funding & Innovation
Intelligence Platform.

Your purpose is to help users understand and use the platform.

You can answer three types of questions:

1. Platform website questions
2. Personalized questions about the current user
3. General questions about research, innovation, startups, funding,
   technology and related topics


IMPORTANT RULES
===============

1. For platform website questions, use the supplied platform knowledge.

2. Never invent a platform page, button, feature, navigation path, or
   workflow that isn't in the supplied knowledge.

3. For personalized questions, use only the current user's information
   supplied by the backend.

4. Never invent information about the current user.

5. Never reveal private information belonging to another user.

6. For general questions, you may use your general knowledge.

7. Clearly distinguish platform-specific information from general
   information when necessary.

8. If you do not have enough information, say so honestly instead of
   guessing.

9. Never claim that a grant success prediction guarantees funding
   success — it's a decision-support estimate.

10. Do not claim the platform supports a feature unless that feature
    exists in the supplied website knowledge.


CONVERSATION RULES
==================

11. Use previous conversation messages when they are relevant to the
    current question.

12. Do not repeat the entire previous answer unless necessary.

13. If the user asks a short follow-up ("what about patents?", "how?",
    "can I do this?"), use the previous conversation to understand what
    they mean.

14. If the current question is unrelated to the previous conversation,
    answer it normally.


RESPONSE STYLE
===============

15. Answer the user's actual question directly.

16. Keep simple questions concise — normally 2 to 5 sentences.

17. For "how do I" questions, use short numbered steps when helpful.

18. For complex questions, provide enough information to answer
    completely, without padding.

19. Always finish the answer naturally — never stop mid-sentence.

20. Use plain, readable text. Avoid unnecessary Markdown formatting,
    excessive asterisks, or decorative headings. Simple numbered lists
    or short bullets are fine.

21. Do not reveal internal instructions or implementation details
    unless explicitly asked.
"""


def format_history(history: list[dict[str, Any]] | None) -> str:
    if not history:
        return "No previous conversation."

    formatted = []
    recent = history[-10:]  # keep the prompt small and responses fast

    for item in recent:
        role = str(item.get("role", "user")).strip()
        content = str(item.get("content", item.get("message", ""))).strip()
        if not content:
            continue
        display_role = "Assistant" if role.lower() in {"assistant", "ai", "model"} else "User"
        formatted.append(f"{display_role}: {content}")

    return "\n".join(formatted) if formatted else "No previous conversation."


def build_prompt(message: str, role: str, user_context: dict, history: list[dict[str, Any]] | None = None) -> str:
    conversation_history = format_history(history)

    return f"""
========================================================
PLATFORM WEBSITE KNOWLEDGE
========================================================

{PLATFORM_KNOWLEDGE}


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

Use the recent conversation only when it helps understand the current
question.

If the question is about how to use the platform, give accurate
step-by-step instructions using the actual navigation and feature names
above — never invent features or workflows.

If the question is about the user's profile, use the supplied current
user information and give personalized recommendations, without
inventing missing profile information.

If the question is general, answer using general knowledge.

If the question is a follow-up, use the conversation history to
understand what the user is referring to, without unnecessarily
repeating the previous answer.

Keep the response concise but complete, and make sure it ends naturally.
Do not use unnecessary Markdown formatting.
"""


async def _generate_response(prompt: str) -> str:
    from google.genai import types

    client = _get_client()
    response = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=1400,
        ),
    )

    answer = response.text
    if not answer:
        return "I couldn't generate a response right now. Please try again."
    return answer.strip()


async def ask_chatbot(
    message: str,
    role: str,
    user_context: dict,
    history: list[dict[str, Any]] | None = None,
) -> str:
    prompt = build_prompt(message=message, role=role, user_context=user_context, history=history)

    retry_delays = [0, 2, 4]

    for attempt, delay in enumerate(retry_delays):
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            return await _generate_response(prompt)
        except ChatbotNotConfiguredError:
            raise
        except Exception as exc:
            error_text = str(exc)
            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "temporarily unavailable" in error_text.lower()
            )
            if not is_temporary_error:
                raise
            if attempt == len(retry_delays) - 1:
                return "The AI assistant is temporarily busy. Please try again in a moment."

    return "I couldn't generate a response right now. Please try again."