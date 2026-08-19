from __future__ import annotations

from app.llm.gemini import llm


VALID_ROUTES = {
    "greeting",
    "rag",
    "web",
    "web_rag",
    "weather",
    "general",
    "ocr",
}


def _clean_route(value: str) -> str:

    value = (
        str(value or "")
        .strip()
        .lower()
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
    )

    for route in VALID_ROUTES:

        if value == route:
            return route

    for route in VALID_ROUTES:

        if route in value.split():
            return route

    return "web"


def classify_intent(
    query: str,
    history: list[dict] | None = None,
    ocr_text: str = "",
    selected_document: str = "",
    document_context: bool = False,
    web_url: str = "",
    web_context: bool = False,
) -> str:

    query = (
        query or ""
    ).strip()

    history = (
        history
        if isinstance(history, list)
        else []
    )

    selected_document = (
        selected_document or ""
    ).strip()

    web_url = (
        web_url or ""
    ).strip()

    if not query:
        return "general"

    history_text = []

    for message in history[-6:]:

        if not isinstance(
            message,
            dict,
        ):
            continue

        role = str(
            message.get(
                "role",
                "user",
            )
        ).upper()

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if content:
            history_text.append(
                f"{role}: {content}"
            )

    history_text = (
        "\n".join(history_text)
        if history_text
        else "No previous conversation."
    )

    # =====================================================
    # CONTEXT DESCRIPTION
    # =====================================================

    if selected_document:

        context_mode = f"""
ACTIVE PDF:
{selected_document}

The user has selected a PDF.

IMPORTANT:
A normal knowledge question must route to RAG.

RAG searches the ENTIRE knowledge base.
Do NOT restrict retrieval to the selected PDF.

If the user explicitly asks for web/current information,
route to WEB.

If the user is simply conversing, route to GENERAL/GREETING.

"""

    elif web_context and web_url:

        context_mode = f"""
ACTIVE WEBPAGE:
{web_url}

The user previously supplied this webpage.

If the current question is about this webpage,
its content, its sections, its products, services,
facts, or anything clearly referring to "it", "this",
"the website", etc.:

route = web_rag

If the current question is unrelated to this webpage:

route = web

Do NOT force unrelated questions into Web RAG.
"""

    else:

        context_mode = """
There is no active PDF and no active webpage.

For factual, informational, current, or knowledge
questions, prefer WEB.

For ordinary conversation, creative tasks, or
non-factual conversation, use GENERAL.

Use GREETING for greetings.

Use WEATHER for weather requests.

Use OCR when the user is asking about available OCR text.
"""

    prompt = f"""
You are the intent classifier of an Agentic RAG assistant.

Return EXACTLY ONE route name.

VALID ROUTES:
greeting
rag
web
web_rag
weather
general
ocr

{context_mode}

CONVERSATION HISTORY:
{history_text}

OCR AVAILABLE:
{bool(ocr_text)}

USER QUESTION:
{query}

ROUTING RULES:

1. If the user is greeting or casually starting/ending
   conversation -> greeting.

2. If the user asks about weather -> weather.

3. If OCR text is available and the question is about
   the image/OCR content -> ocr.

4. If an active PDF exists and the question is a normal
   knowledge/document question -> rag.

5. If an active PDF exists but the user explicitly wants
   web/current information -> web.

6. If an active webpage exists:
   - webpage-related question -> web_rag
   - unrelated question -> web

7. Without any active context:
   - factual/informational/current -> web
   - normal conversation/creative -> general

8. Never return explanations.
9. Return only one route.

ROUTE:
"""

    try:

        result = llm.generate(
            prompt
        )

        return _clean_route(
            result
        )

    except Exception as error:

        print(
            "[CLASSIFIER ERROR]",
            repr(error),
        )

        # Safe fallback for factual questions.
        return "web"