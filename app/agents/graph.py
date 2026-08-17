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


# =========================================================
# VALID ROUTES
# =========================================================
#
# These MUST match the routes supported by supervisor.py.
#
# IMPORTANT:
#
# web       = normal Web Search
#
# web_rag   = user-provided URL -> Web RAG
#
# They are two completely different routes.
#
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
# ROUTE AFTER SUPERVISOR
# =========================================================
#
# IMPORTANT:
#
# The supervisor decides the route.
#
# graph.py ONLY executes that route.
#
# graph.py MUST NOT:
#
# - inspect URLs
# - run another classifier
# - convert web_rag -> web
# - inspect documents
# - inspect greetings
# - inspect weather
#
# =========================================================

def route_after_supervisor(
    state: AgentState,
) -> Literal[
    "rag",
    "web_rag",
    "web",
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

    # =====================================================
    # BACKWARD COMPATIBILITY
    # =====================================================
    #
    # These are only old aliases.
    #
    # CRITICAL:
    #
    # web_rag MUST NOT be converted to web.
    #
    # web_rag is now a real execution route.
    #
    # =====================================================

    if route == "document_rag":

        route = "rag"

    elif route == "document":

        route = "rag"

    elif route == "knowledge":

        route = "rag"

    # =====================================================
    # VALIDATE
    # =====================================================

    if route not in VALID_ROUTES:

        print(
            "[GRAPH] Invalid supervisor route:",
            route,
        )

        route = "general"

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n================ GRAPH ================"
    )

    print(
        "Supervisor selected:",
        route,
    )

    print(
        "Executing node:",
        route,
    )

    print(
        "=======================================\n"
    )

    return route


# =========================================================
# GRAPH
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

# ---------------------------------------------------------
# PDF RAG
# ---------------------------------------------------------

builder.add_node(
    "rag",
    rag_node,
)


# ---------------------------------------------------------
# NORMAL WEB SEARCH
# ---------------------------------------------------------
#
# User asks:
#
# "latest AI news"
# "search the web for..."
#
# -> web
#
# ---------------------------------------------------------

builder.add_node(
    "web",
    web_node,
)


# ---------------------------------------------------------
# WEB RAG
# ---------------------------------------------------------
#
# User provides:
#
# https://www.example.com
#
# -> web_rag
#
# URL
#   ↓
# scrape
#   ↓
# clean
#   ↓
# chunk
#   ↓
# embed
#   ↓
# retrieve
#   ↓
# LLM
#
# ---------------------------------------------------------

builder.add_node(
    "web_rag",
    web_rag_node,
)


# ---------------------------------------------------------
# WEATHER
# ---------------------------------------------------------

builder.add_node(
    "weather",
    weather_node,
)


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

builder.add_node(
    "ocr",
    ocr_node,
)


# ---------------------------------------------------------
# GREETING
# ---------------------------------------------------------

builder.add_node(
    "greeting",
    greeting_node,
)


# ---------------------------------------------------------
# GENERAL AI
# ---------------------------------------------------------

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
# SUPERVISOR → EXECUTION
# =========================================================
#
# IMPORTANT:
#
# Every supervisor route has its own execution node.
#
# In particular:
#
#     web_rag -> web_rag
#
# NOT:
#
#     web_rag -> web
#
# =========================================================

builder.add_conditional_edges(
    "supervisor",

    route_after_supervisor,

    {
        "rag": "rag",

        "web_rag": "web_rag",

        "web": "web",

        "weather": "weather",

        "ocr": "ocr",

        "greeting": "greeting",

        "general": "general",
    },
)


# =========================================================
# EXECUTION → END
# =========================================================

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