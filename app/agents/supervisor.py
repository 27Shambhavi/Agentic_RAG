from __future__ import annotations

import re

from app.agents.state import AgentState
from app.agents.classifier import classify_intent


# =========================================================
# VALID ROUTES
# =========================================================

VALID_ROUTES = {
    "rag",
    "web_rag",
    "web",
    "weather",
    "ocr",
    "greeting",
    "general",
}


# =========================================================
# GREETING
# =========================================================

def is_greeting(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "wassup",
        "what's up",
        "whats up",
    }

    return q in greetings


# =========================================================
# WEATHER
# =========================================================

def is_weather_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    weather_words = {
        "weather",
        "temperature",
        "forecast",
        "rain",
        "raining",
        "snow",
        "humidity",
    }

    return any(
        word in q
        for word in weather_words
    )


# =========================================================
# EXPLICIT WEB SEARCH
# =========================================================
#
# IMPORTANT:
#
# This means NORMAL web search.
#
# It is different from Web RAG.
#
# Examples:
#
# "search the web for latest AI news"
# "latest news about OpenAI"
#
# -> WEB
#
# =========================================================

def is_explicit_web_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    if not q:
        return False

    web_patterns = (

        # -------------------------------------------------
        # Explicit search
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Current information
        # -------------------------------------------------

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
        for pattern in web_patterns
    )


# =========================================================
# URL DETECTION
# =========================================================
#
# Detect:
#
# https://example.com
# http://example.com
#
# Also handles a URL followed by punctuation.
#
# =========================================================

def extract_url(
    query: str,
) -> str:

    q = (
        query or ""
    ).strip()

    if not q:
        return ""

    pattern = r"""https?://[^\s<>"']+"""

    match = re.search(
        pattern,
        q,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    url = (
        match.group(0)
        .strip()
        .rstrip(
            ".,!?;:)]}"
        )
    )

    return url


# =========================================================
# SUPERVISOR
# =========================================================

def supervisor(
    state: AgentState,
) -> AgentState:

    # =====================================================
    # INPUT
    # =====================================================

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
        state.get(
            "document_context",
            False,
        )
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

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,

            "route": "general",

            "answer": "",

            "sources": [],
        }

    # =====================================================
    # URL IN CURRENT QUERY
    # =====================================================

    detected_url = extract_url(
        query
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n================================================"
    )

    print(
        "                 SUPERVISOR"
    )

    print(
        "================================================"
    )

    print(
        "User query:",
        query,
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    print(
        "Document context:",
        document_context,
    )

    print(
        "State Web URL:",
        web_url or "NONE",
    )

    print(
        "URL in current query:",
        detected_url or "NONE",
    )

    print(
        "OCR available:",
        bool(ocr_text),
    )

    print(
        "History messages:",
        len(history),
    )

    print(
        "================================================"
    )

    # =====================================================
    # PRIORITY 1
    # CURRENT MESSAGE CONTAINS URL
    # =====================================================
    #
    # THIS IS THE MOST IMPORTANT RULE.
    #
    # If the user gives a URL in the current message:
    #
    #     URL
    #      ↓
    #   WEB_RAG
    #
    # It must NEVER become normal WEB search.
    #
    # Example:
    #
    # https://www.magicbricks.com/
    #
    # -> web_rag
    #
    # Even if:
    #
    # "latest information"
    #
    # appears in the same query.
    #
    # =====================================================

    if detected_url:

        print(
            "\n[SUPERVISOR]"
        )

        print(
            "CURRENT URL DETECTED"
        )

        print(
            "URL:",
            detected_url,
        )

        print(
            "FORCED ROUTE: WEB_RAG"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "web_rag",

            "web_url": detected_url,

            "web_context": True,
        }

    # =====================================================
    # PRIORITY 2
    # EXISTING WEB RAG URL
    # =====================================================
    #
    # This handles follow-up questions.
    #
    # Example:
    #
    # First:
    #
    # https://www.magicbricks.com/
    #
    # Second:
    #
    # "What services does it provide?"
    #
    # If no PDF is active, reuse the Web RAG URL.
    #
    # =====================================================

    if (
        web_url
        and not selected_document
    ):

        print(
            "\n[SUPERVISOR]"
        )

        print(
            "EXISTING WEB RAG URL"
        )

        print(
            "URL:",
            web_url,
        )

        print(
            "No active PDF."
        )

        print(
            "FORCED ROUTE: WEB_RAG"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "web_rag",

            "web_url": web_url,

            "web_context": True,
        }

    # =====================================================
    # PRIORITY 3
    # ACTIVE PDF
    # =====================================================
    #
    # This is the protection against the exact problem
    # you were facing.
    #
    # Example:
    #
    # Previous Web RAG:
    #
    #     https://www.magicbricks.com/
    #
    # Then user selects:
    #
    #     Ayushman Bharat Yojna.pdf
    #
    # Then asks:
    #
    #     "what are the schemes?"
    #
    # Frontend/backend might still contain the old URL.
    #
    # We IGNORE it.
    #
    # Result:
    #
    #     PDF -> RAG
    #
    # =====================================================

    if (
        selected_document
        and document_context
    ):

        if web_url:

            print(
                "\n[SUPERVISOR]"
            )

            print(
                "ACTIVE PDF DETECTED"
            )

            print(
                "Ignoring stale Web URL:",
                web_url,
            )

            print(
                "The old URL WILL NOT be used."
            )

            print(
                "================================================"
            )

        print(
            "[SUPERVISOR] ACTIVE PDF -> RAG"
        )

        print(
            "[SUPERVISOR] Classifier bypassed."
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "rag",

            "selected_document": (
                selected_document
            ),

            "document_context": True,

            # -------------------------------------------------
            # CRITICAL
            # -------------------------------------------------
            #
            # Remove stale Web RAG state.
            #
            "web_url": "",

            "web_context": False,
        }

    # =====================================================
    # PRIORITY 4
    # OCR
    # =====================================================

    if ocr_text:

        print(
            "[SUPERVISOR] OCR context -> OCR"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "ocr",

            "ocr_text": ocr_text,
        }

    # =====================================================
    # PRIORITY 5
    # WEATHER
    # =====================================================

    if is_weather_request(
        query
    ):

        print(
            "[SUPERVISOR] Weather -> WEATHER"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "weather",
        }

    # =====================================================
    # PRIORITY 6
    # GREETING
    # =====================================================

    if is_greeting(
        query
    ):

        print(
            "[SUPERVISOR] Greeting -> GREETING"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "greeting",
        }

    # =====================================================
    # PRIORITY 7
    # EXPLICIT NORMAL WEB SEARCH
    # =====================================================
    #
    # IMPORTANT:
    #
    # We reach this point ONLY when:
    #
    # - no URL in current query
    # - no active Web RAG URL
    # - no active PDF
    #
    # Therefore this is genuinely normal Web Search.
    #
    # =====================================================

    if is_explicit_web_request(
        query
    ):

        print(
            "[SUPERVISOR] Explicit web search -> WEB"
        )

        print(
            "================================================\n"
        )

        return {
            **state,

            "route": "web",

            "web_url": "",

            "web_context": False,
        }

    # =====================================================
    # PRIORITY 8
    # CLASSIFIER
    # =====================================================
    #
    # At this point there is:
    #
    # - no URL
    # - no active Web RAG URL
    # - no active PDF
    # - no OCR
    # - no weather
    # - no greeting
    # - no explicit web request
    #
    # NOW classifier is allowed to decide.
    #
    # =====================================================

    try:

        route = classify_intent(
            query=query,

            history=history,

            ocr_text=ocr_text,

            selected_document="",

            document_context=False,
        )

        route = (
            route
            or "general"
        ).strip().lower()

    except Exception as error:

        print(
            "[SUPERVISOR CLASSIFIER ERROR]"
        )

        print(
            repr(error)
        )

        route = "general"

    # =====================================================
    # CLEAN CLASSIFIER OUTPUT
    # =====================================================

    route = (
        route
        .replace(
            "`",
            "",
        )
        .replace(
            '"',
            "",
        )
        .replace(
            "'",
            "",
        )
        .strip()
        .lower()
    )

    # =====================================================
    # SAFETY:
    # CLASSIFIER MUST NOT INVENT WEB_RAG
    #
    # If there is no URL, classifier cannot legitimately
    # choose Web RAG.
    #
    # =====================================================

    if route == "web_rag":

        print(
            "[SUPERVISOR] Classifier returned WEB_RAG "
            "without a URL."
        )

        print(
            "[SUPERVISOR] Converting to GENERAL."
        )

        route = "general"

    # =====================================================
    # VALIDATE ROUTE
    # =====================================================

    if route not in VALID_ROUTES:

        print(
            "[SUPERVISOR] Invalid route:",
            route,
        )

        route = "general"

    # =====================================================
    # FINAL DEBUG
    # =====================================================

    print(
        "\n[SUPERVISOR] FINAL ROUTE:",
        route,
    )

    print(
        "[SUPERVISOR] FINAL WEB URL:",
        web_url or "NONE",
    )

    print(
        "[SUPERVISOR] FINAL DOCUMENT:",
        selected_document or "NONE",
    )

    print(
        "================================================\n"
    )

    # =====================================================
    # FINAL STATE
    # =====================================================

    return {
        **state,

        "route": route,

        "selected_document": (
            selected_document
        ),

        "document_context": (
            document_context
        ),

        "ocr_text": (
            ocr_text
        ),

        "history": (
            history
        ),

        "web_url": (
            web_url
        ),

        "web_context": bool(
            web_url
        ),
    }