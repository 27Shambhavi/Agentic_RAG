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


VALID_ROUTES = {
    "rag",
    "web",
    "web_rag",
    "weather",
    "ocr",
    "greeting",
    "general",
}


# =========================================================
# SUPERVISOR -> EXECUTION
# =========================================================

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
            "[GRAPH] Invalid route:",
            route,
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


# =========================================================
# RAG -> END / WEB
# =========================================================

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

    if rag_found:

        print(
            "[GRAPH] RAG SUCCESS -> END"
        )

        return "end"

    print(
        "[GRAPH] RAG NOT FOUND -> WEB"
    )

    return "web"


# =========================================================
# BUILD
# =========================================================

builder = StateGraph(
    AgentState
)


# =========================================================
# NODES
# =========================================================

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


# =========================================================
# START
# =========================================================

builder.add_edge(
    START,
    "supervisor",
)


# =========================================================
# SUPERVISOR ROUTING
# =========================================================

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


# =========================================================
# RAG FALLBACK
# =========================================================

builder.add_conditional_edges(

    "rag",

    route_after_rag,

    {
        "end": END,

        "web": "web",
    },
)


# =========================================================
# OTHER NODES
# =========================================================

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


# =========================================================
# COMPILE
# =========================================================

agent = builder.compile()

print(
    "[GRAPH] Agent graph compiled successfully."
)