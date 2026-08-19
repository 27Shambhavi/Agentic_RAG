from __future__ import annotations

import re

from app.agents.state import AgentState
from app.agents.classifier import classify_intent


VALID_ROUTES = {
    "greeting",
    "rag",
    "web",
    "web_rag",
    "weather",
    "general",
    "ocr",
}


URL_PATTERN = re.compile(
    r"https?://[^\s<>'\"`]+",
    re.IGNORECASE,
)


def extract_url(
    query: str,
) -> str:

    query = (
        query or ""
    ).strip()

    if not query:
        return ""

    match = URL_PATTERN.search(
        query
    )

    if not match:
        return ""

    return (
        match.group(0)
        .strip()
        .rstrip(
            ".,!?;:)]}"
        )
    )


def is_explicit_web_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    patterns = (
        "search the web",
        "search web",
        "search the internet",
        "search internet",
        "search online",
        "look it up online",
        "look it up on the internet",
        "find it online",
        "google it",
        "google this",
        "browse the web",
        "browse online",
        "latest news",
        "latest update",
        "latest information",
        "today's news",
        "today news",
        "current news",
        "breaking news",
        "recent news",
        "what happened today",
        "what is happening today",
        "current information",
        "current status",
        "current update",
        "live information",
    )

    return any(
        pattern in q
        for pattern in patterns
    )


def supervisor(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    selected_document = (
        state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    document_context = bool(
        selected_document
    )

    ocr_text = (
        state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    history = state.get(
        "history",
        [],
    )

    if not isinstance(
        history,
        list,
    ):
        history = []

    web_url = (
        state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

    web_context = bool(
        web_url
    )

    if not query:

        return {
            **state,
            "route": "general",
            "answer": "",
            "sources": [],
        }

    detected_url = extract_url(
        query
    )

    print(
        "\n================ SUPERVISOR ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected PDF:",
        selected_document or "NONE",
    )

    print(
        "Existing Web URL:",
        web_url or "NONE",
    )

    print(
        "Current URL:",
        detected_url or "NONE",
    )

    # =====================================================
    # 1. CURRENT URL
    # =====================================================
    #
    # Explicit URL always means Web RAG.
    #
    # =====================================================

    if detected_url:

        print(
            "[SUPERVISOR] Current URL -> WEB_RAG"
        )

        return {
            **state,

            "route": "web_rag",

            "web_url": detected_url,

            "web_context": True,
        }

    # =====================================================
    # 2. EXPLICIT NORMAL WEB SEARCH
    # =====================================================

    if is_explicit_web_request(
        query
    ):

        print(
            "[SUPERVISOR] Explicit web request -> WEB"
        )

        return {
            **state,

            "route": "web",

            # Preserve URL in state.
            "web_url": web_url,

            "web_context": False,
        }

    # =====================================================
    # 3. CLASSIFIER
    # =====================================================
    #
    # Classifier decides:
    #
    # greeting
    # weather
    # ocr
    # rag
    # web
    # web_rag
    # general
    #
    # =====================================================

    try:

        route = classify_intent(

            query=query,

            history=history,

            ocr_text=ocr_text,

            selected_document=selected_document,

            document_context=document_context,

            web_url=web_url,

            web_context=web_context,
        )

    except Exception as error:

        print(
            "[SUPERVISOR CLASSIFIER ERROR]",
            repr(error),
        )

        route = "web"

    route = (
        str(route or "web")
        .strip()
        .lower()
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
    )

    # =====================================================
    # 4. ACTIVE PDF
    # =====================================================
    #
    # If PDF exists and classifier says normal knowledge,
    # RAG gets first chance.
    #
    # If RAG fails, GRAPH -> WEB.
    #
    # =====================================================

    if selected_document:

        if route in {
            "greeting",
            "weather",
            "ocr",
            "general",
        }:

            final_route = route

        elif route == "web":

            final_route = "web"

        else:

            final_route = "rag"

        print(
            "[SUPERVISOR] PDF active ->",
            final_route,
        )

        return {
            **state,

            "route": final_route,

            "selected_document": selected_document,

            "document_context": True,

            # Preserve old URL.
            #
            # But do not activate Web RAG while PDF
            # is the active context.
            "web_url": web_url,

            "web_context": False,
        }

    # =====================================================
    # 5. ACTIVE WEBPAGE
    # =====================================================
    #
    # Classifier decides:
    #
    # related -> web_rag
    # unrelated -> web
    #
    # =====================================================

    if web_url:

        if route == "web_rag":

            final_route = "web_rag"

        else:

            final_route = "web"

        print(
            "[SUPERVISOR] Existing webpage ->",
            final_route,
        )

        return {
            **state,

            "route": final_route,

            "web_url": web_url,

            "web_context": (
                final_route == "web_rag"
            ),
        }

    # =====================================================
    # 6. NO ACTIVE CONTEXT
    # =====================================================

    if route not in VALID_ROUTES:

        route = "web"

    print(
        "[SUPERVISOR] FINAL ROUTE:",
        route,
    )

    return {
        **state,

        "route": route,

        "selected_document": "",

        "document_context": False,

        "web_url": "",

        "web_context": False,

        "ocr_text": ocr_text,

        "history": history,
    }