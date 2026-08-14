from typing import Literal

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
    weather_node,
    ocr_node,
)


# =========================================================
# EXPLICIT WEB REQUEST DETECTION
# =========================================================
#
# Web is allowed ONLY when the user explicitly asks for
# current / online / internet information.
#
# If a document is selected and the user asks a normal
# question, RAG gets priority.
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
        "search the web",
        "search web",
        "search the internet",
        "search online",
        "look it up online",
        "look it up on the internet",
        "find it online",
        "google it",
        "latest",
        "today's news",
        "today news",
        "current news",
        "breaking news",
        "recent news",
        "what is happening today",
        "what happened today",
        "current information",
        "current status",
        "live information",
    )

    return any(
        pattern in q
        for pattern in web_patterns
    )


# =========================================================
# ROUTE AFTER SUPERVISOR
# =========================================================

def route_after_supervisor(
    state: AgentState,
) -> Literal[
    "greeting",
    "rag",
    "web",
    "weather",
    "ocr",
    "general",
]:

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

    supervisor_route = (
        state.get(
            "route",
            "general",
        )
        or "general"
    ).strip().lower()

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
        "Supervisor route:",
        supervisor_route,
    )

    # =====================================================
    # OCR HAS HIGHEST PRIORITY
    # =====================================================

    if supervisor_route == "ocr":

        print(
            "[GRAPH] Route -> OCR"
        )

        return "ocr"

    # =====================================================
    # WEATHER
    # =====================================================

    if supervisor_route == "weather":

        print(
            "[GRAPH] Route -> WEATHER"
        )

        return "weather"

    # =====================================================
    # EXPLICIT WEB REQUEST
    #
    # Example:
    #
    # "search the web for..."
    # "latest news about..."
    # "what happened today..."
    #
    # This is the ONLY normal way an active document
    # conversation should go to WEB.
    # =====================================================

    if is_explicit_web_request(
        query
    ):

        print(
            "[GRAPH] Explicit web request -> WEB"
        )

        return "web"

    # =====================================================
    # ACTIVE DOCUMENT
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # If a document is selected, normal questions go
    # directly to RAG.
    #
    # We DO NOT trust an ambiguous supervisor decision
    # such as "web".
    # =====================================================

    if selected_document and document_context:

        print(
            "[GRAPH] Active document detected."
        )

        print(
            "[GRAPH] Normal document question -> RAG"
        )

        return "rag"

    # =====================================================
    # NO ACTIVE DOCUMENT
    #
    # Now supervisor decision is trusted.
    # =====================================================

    if supervisor_route == "greeting":

        print(
            "[GRAPH] Route -> GREETING"
        )

        return "greeting"

    if supervisor_route == "rag":

        print(
            "[GRAPH] Route -> RAG"
        )

        return "rag"

    if supervisor_route == "web":

        print(
            "[GRAPH] Route -> WEB"
        )

        return "web"

    if supervisor_route == "general":

        print(
            "[GRAPH] Route -> GENERAL"
        )

        return "general"

    # =====================================================
    # SAFE FALLBACK
    # =====================================================

    print(
        "[GRAPH] Unknown route -> GENERAL"
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
# SUPERVISOR → EXECUTION ROUTE
# =========================================================

builder.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {
        "greeting": "greeting",
        "rag": "rag",
        "web": "web",
        "weather": "weather",
        "ocr": "ocr",
        "general": "general",
    },
)


# =========================================================
# EXECUTION → END
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