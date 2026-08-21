from __future__ import annotations

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
    web_rag_node,
    weather_node,
    ocr_node,
)


# ============================================================
# VALID ROUTES
# ============================================================

VALID_ROUTES = {
    "rag",
    "web",
    "web_rag",
    "weather",
    "ocr",
    "greeting",
    "general",
}


# ============================================================
# SUPERVISOR ROUTING
# ============================================================

def route_after_supervisor(
    state: AgentState,
) -> Literal[
    "rag",
    "web",
    "web_rag",
    "weather",
    "ocr",
    "greeting",
    "general",
]:

    route = (
        state.get(
            "route",
            "general",
        )
        or "general"
    )

    route = (
        str(route)
        .strip()
        .lower()
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
    )

    # Optional aliases.
    aliases = {
        "document": "rag",
        "document_rag": "rag",
        "knowledge": "rag",
    }

    route = aliases.get(
        route,
        route,
    )

    if route not in VALID_ROUTES:

        print(
            "[GRAPH] Invalid supervisor route -> general:",
            repr(route),
        )

        route = "general"

    print(
        "\n================ GRAPH ================"
    )

    print(
        "Supervisor route:",
        route,
    )

    print(
        "=======================================\n"
    )

    return route


# ============================================================
# AFTER RAG
# ============================================================

def route_after_rag(
    state: AgentState,
) -> Literal[
    "end",
    "web",
]:

    rag_found = bool(
        state.get(
            "rag_found",
            False,
        )
    )

    # --------------------------------------------------------
    # RAG SUCCESS
    # --------------------------------------------------------

    if rag_found:

        print(
            "[GRAPH] RAG SUCCESS -> END"
        )

        return "end"

    # --------------------------------------------------------
    # RAG FAILED RELEVANCE
    # --------------------------------------------------------

    print(
        "[GRAPH] RAG NOT FOUND -> WEB"
    )

    return "web"


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(
    AgentState
)


# ============================================================
# NODES
# ============================================================

builder.add_node(
    "supervisor",
    supervisor,
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
    "web_rag",
    web_rag_node,
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
    "greeting",
    greeting_node,
)

builder.add_node(
    "general",
    general_node,
)


# ============================================================
# START
# ============================================================

builder.add_edge(
    START,
    "supervisor",
)


# ============================================================
# SUPERVISOR -> ROUTE
# ============================================================

builder.add_conditional_edges(
    "supervisor",

    route_after_supervisor,

    {
        "rag": "rag",

        "web": "web",

        "web_rag": "web_rag",

        "weather": "weather",

        "ocr": "ocr",

        "greeting": "greeting",

        "general": "general",
    },
)


# ============================================================
# RAG -> END OR WEB
# ============================================================
#
# RAG is deliberately two-stage:
#
#        RAG retrieval
#              |
#              v
#       relevance check
#          /       \
#        YES       NO
#         |         |
#         v         v
#        END       WEB
#
# This implements:
#
# "Search knowledge base first.
#  If not relevant, search web."
#
# ============================================================

builder.add_conditional_edges(
    "rag",

    route_after_rag,

    {
        "end": END,

        "web": "web",
    },
)


# ============================================================
# TERMINAL EDGES
# ============================================================

builder.add_edge(
    "web",
    END,
)

builder.add_edge(
    "web_rag",
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
    "greeting",
    END,
)

builder.add_edge(
    "general",
    END,
)


# ============================================================
# COMPILE
# ============================================================

agent = builder.compile()


print(
    "[GRAPH] Agent graph compiled successfully."
)