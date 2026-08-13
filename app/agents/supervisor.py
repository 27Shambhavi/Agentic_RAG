from app.agents.state import AgentState
from app.agents.classifier import classify_intent


# =========================================================
# SUPERVISOR
# =========================================================

def supervisor(
    state: AgentState,
) -> AgentState:

    query = state.get(
        "query",
        "",
    ).strip()

    # -----------------------------------------------------
    # EMPTY QUERY
    # -----------------------------------------------------

    if not query:

        return {
            **state,
            "route": "general",
        }

    # -----------------------------------------------------
    # CLASSIFY USER INTENT
    # -----------------------------------------------------

    route = classify_intent(
        query
    )

    # -----------------------------------------------------
    # UPDATE STATE
    # -----------------------------------------------------

    return {
        **state,
        "route": route,
    }