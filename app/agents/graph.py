from typing import Literal

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agents.state import (
    AgentState
)

from app.agents.nodes import (
    supervisor_node,
    greeting_node,
    general_node,
    rag_node,
    web_node,
)


# =========================================================
# ROUTE AFTER LOCAL SUPERVISOR
# =========================================================

def route_after_supervisor(
    state: AgentState
) -> Literal[
    "greeting",
    "rag",
    "web",
    "general",
]:

    route = state.get(
        "route",
        "general"
    )

    if route == "greeting":
        return "greeting"

    if route == "rag":
        return "rag"

    if route == "web":
        return "web"

    return "general"


# =========================================================
# GRAPH
# =========================================================

builder = StateGraph(
    AgentState
)


# =========================================================
# NODES
# =========================================================

builder.add_node(
    "supervisor",
    supervisor_node
)

builder.add_node(
    "greeting",
    greeting_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "web",
    web_node
)

builder.add_node(
    "general",
    general_node
)


# =========================================================
# START
# =========================================================

builder.add_edge(
    START,
    "supervisor"
)


# =========================================================
# CONDITIONAL ROUTING
# =========================================================

builder.add_conditional_edges(
    "supervisor",

    route_after_supervisor,

    {
        "greeting": "greeting",
        "rag": "rag",
        "web": "web",
        "general": "general",
    }
)


# =========================================================
# END
# =========================================================

builder.add_edge(
    "greeting",
    END
)

builder.add_edge(
    "rag",
    END
)

builder.add_edge(
    "web",
    END
)

builder.add_edge(
    "general",
    END
)


# =========================================================
# COMPILE
# =========================================================

agent = builder.compile()