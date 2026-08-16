from typing import Literal
import re

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agents.state import AgentState
from app.agents.supervisor import supervisor

from app.agents.nodes import (
    greeting_node,
    general_node,
    rag_node,
    web_node,
    web_rag_node,
    weather_node,
    ocr_node,
)


# =========================================================
# URL EXTRACTION
# =========================================================

def extract_url(query: str) -> str:

    query = (
        query or ""
    ).strip()

    if not query:
        return ""

    # -----------------------------------------------------
    # MARKDOWN URL
    #
    # [Example](https://example.com)
    # -----------------------------------------------------

    markdown_pattern = (
        r"\[[^\]]*\]"
        r"\("
        r"(https?://[^\s\)]+)"
        r"\)"
    )

    match = re.search(
        markdown_pattern,
        query,
        flags=re.IGNORECASE,
    )

    if match:

        return (
            match.group(1)
            .strip()
            .rstrip(
                ".,!?;:)]}"
            )
        )

    # -----------------------------------------------------
    # NORMAL URL
    # -----------------------------------------------------

    url_pattern = (
        r"https?://[^\s<>\"']+"
    )

    match = re.search(
        url_pattern,
        query,
        flags=re.IGNORECASE,
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


# =========================================================
# EXPLICIT WEB SEARCH DETECTION
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

        # Explicit search
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

        # Current information
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
# GREETING DETECTION
# =========================================================
#
# IMPORTANT:
#
# This prevents an active PDF from hijacking simple
# conversational messages such as:
#
# hello
# hi
# hey
# good morning
# thanks
# thank you
#
# These should remain general conversation and NOT
# become PDF RAG merely because a document is selected.
#
# =========================================================

def is_greeting_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    if not q:
        return False

    # Remove simple punctuation.
    cleaned = re.sub(
        r"[^\w\s']",
        " ",
        q,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    greeting_phrases = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "helloo",
        "hellooo",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "thanks",
        "thank you",
        "thankyou",
        "thx",
        "ty",
        "bye",
        "goodbye",
    }

    if cleaned in greeting_phrases:
        return True

    return False


# =========================================================
# ROUTER
# =========================================================

def route_after_supervisor(
    state: AgentState,
) -> Literal[
    "greeting",
    "rag",
    "web_rag",
    "web",
    "weather",
    "ocr",
    "general",
]:

    # =====================================================
    # QUERY
    # =====================================================

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # SELECTED DOCUMENT
    # =====================================================

    selected_document = (
        state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # DOCUMENT CONTEXT
    # =====================================================

    document_context = bool(
        state.get(
            "document_context",
            False,
        )
    )

    # =====================================================
    # SUPERVISOR ROUTE
    # =====================================================

    supervisor_route = (
        state.get(
            "route",
            "general",
        )
        or "general"
    ).strip().lower()

    # =====================================================
    # WEB URL FROM STATE
    # =====================================================

    web_url = (
        state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # NORMALIZE URL FROM STATE
    # =====================================================

    if web_url:

        normalized_url = extract_url(
            web_url
        )

        if normalized_url:

            web_url = normalized_url

    # =====================================================
    # DETECT URL FROM USER QUERY
    # =====================================================

    if not web_url:

        web_url = extract_url(
            query
        )

    # =====================================================
    # EXPLICIT WEB SEARCH
    # =====================================================

    explicit_web = is_explicit_web_request(
        query
    )

    # =====================================================
    # DIRECT GREETING DETECTION
    # =====================================================

    direct_greeting = is_greeting_request(
        query
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n================ GRAPH ROUTER ================"
    )

    print(
        "Query:",
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
        "Detected URL:",
        web_url or "NONE",
    )

    print(
        "Explicit web request:",
        explicit_web,
    )

    print(
        "Direct greeting:",
        direct_greeting,
    )

    print(
        "Supervisor route:",
        supervisor_route,
    )

    # =====================================================
    # PRIORITY 1 — USER PROVIDED URL
    # =====================================================
    #
    # URL ALWAYS means WEB RAG.
    #
    # This has the highest priority because an explicit
    # webpage supplied by the user is a strong signal.
    #
    # PDF selection does NOT override a URL.
    #
    # Example:
    #
    # PDF selected
    # +
    # What is redBus?
    # https://www.redbus.in/
    #
    # -> WEB RAG
    #
    # =====================================================

    if web_url:

        print(
            "[GRAPH] URL detected."
        )

        print(
            "[GRAPH] Route -> WEB RAG"
        )

        print(
            "================================================\n"
        )

        return "web_rag"

    # =====================================================
    # PRIORITY 2 — EXPLICIT WEB SEARCH
    # =====================================================
    #
    # Example:
    #
    # PDF selected
    #
    # "Search the web for latest AI news"
    #
    # -> WEB
    #
    # =====================================================

    if explicit_web:

        print(
            "[GRAPH] Explicit web search request."
        )

        print(
            "[GRAPH] Route -> WEB"
        )

        print(
            "================================================\n"
        )

        return "web"

    # =====================================================
    # PRIORITY 3 — OCR
    # =====================================================

    if supervisor_route == "ocr":

        print(
            "[GRAPH] Route -> OCR"
        )

        print(
            "================================================\n"
        )

        return "ocr"

    # =====================================================
    # PRIORITY 4 — WEATHER
    # =====================================================

    if supervisor_route == "weather":

        print(
            "[GRAPH] Route -> WEATHER"
        )

        print(
            "================================================\n"
        )

        return "weather"

    # =====================================================
    # PRIORITY 5 — GREETING
    # =====================================================
    #
    # IMPORTANT:
    #
    # GREETING MUST COME BEFORE ACTIVE PDF.
    #
    # Otherwise:
    #
    # PDF selected
    # +
    # "hello"
    #
    # would incorrectly become:
    #
    # hello -> PDF RAG
    #
    # =====================================================

    if (
        direct_greeting
        or supervisor_route == "greeting"
    ):

        print(
            "[GRAPH] Greeting detected."
        )

        print(
            "[GRAPH] Route -> GREETING"
        )

        print(
            "================================================\n"
        )

        return "greeting"

    # =====================================================
    # PRIORITY 6 — ACTIVE PDF
    # =====================================================
    #
    # NOW the PDF gets its priority.
    #
    # This means:
    #
    # PDF selected
    # +
    # normal document question
    #
    # -> RAG
    #
    # But:
    #
    # hello
    # -> greeting
    #
    # URL
    # -> web_rag
    #
    # explicit web search
    # -> web
    #
    # =====================================================

    if (
        selected_document
        and document_context
    ):

        print(
            "[GRAPH] Active PDF detected."
        )

        print(
            "[GRAPH] Normal question -> RAG"
        )

        print(
            "[GRAPH] Supervisor route:",
            supervisor_route,
        )

        print(
            "================================================\n"
        )

        return "rag"

    # =====================================================
    # PRIORITY 7 — SUPERVISOR RAG
    # =====================================================

    if supervisor_route == "rag":

        print(
            "[GRAPH] Route -> RAG"
        )

        print(
            "================================================\n"
        )

        return "rag"

    # =====================================================
    # PRIORITY 8 — SUPERVISOR WEB
    # =====================================================

    if supervisor_route == "web":

        print(
            "[GRAPH] Route -> WEB"
        )

        print(
            "================================================\n"
        )

        return "web"

    # =====================================================
    # PRIORITY 9 — SUPERVISOR GENERAL
    # =====================================================

    if supervisor_route == "general":

        print(
            "[GRAPH] Route -> GENERAL"
        )

        print(
            "================================================\n"
        )

        return "general"

    # =====================================================
    # FALLBACK
    # =====================================================

    print(
        "[GRAPH] Unknown route -> GENERAL"
    )

    print(
        "================================================\n"
    )

    return "general"


# =========================================================
# CREATE GRAPH
# =========================================================

builder = StateGraph(
    AgentState
)


# =========================================================
# SUPERVISOR
# =========================================================

builder.add_node(
    "supervisor",
    supervisor,
)


# =========================================================
# EXECUTION NODES
# =========================================================

builder.add_node(
    "greeting",
    greeting_node,
)

builder.add_node(
    "rag",
    rag_node,
)

builder.add_node(
    "web_rag",
    web_rag_node,
)

builder.add_node(
    "web",
    web_node,
)

builder.add_node(
    "weather",
    weather_node,
)

builder.add_node(
    "ocr",
    ocr_node,
)

builder.add_node(
    "general",
    general_node,
)


# =========================================================
# START
# =========================================================

builder.add_edge(
    START,
    "supervisor",
)


# =========================================================
# SUPERVISOR -> EXECUTION
# =========================================================

builder.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {
        "greeting": "greeting",
        "rag": "rag",
        "web_rag": "web_rag",
        "web": "web",
        "weather": "weather",
        "ocr": "ocr",
        "general": "general",
    },
)


# =========================================================
# EXECUTION -> END
# =========================================================

builder.add_edge(
    "greeting",
    END,
)

builder.add_edge(
    "rag",
    END,
)

builder.add_edge(
    "web_rag",
    END,
)

builder.add_edge(
    "web",
    END,
)

builder.add_edge(
    "weather",
    END,
)

builder.add_edge(
    "ocr",
    END,
)

builder.add_edge(
    "general",
    END,
)


# =========================================================
# COMPILE
# =========================================================

agent = builder.compile()