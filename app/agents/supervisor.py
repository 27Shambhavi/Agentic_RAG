from __future__ import annotations

import re

from app.agents.state import AgentState
from app.agents.prompts import SUPERVISOR_PROMPT
from app.llm.gemini import llm


# =========================================================
# VALID ROUTES
# =========================================================

VALID_ROUTES = {
    "greeting",
    "rag",
    "web",
    "web_rag",
    "general",
    "weather",
    "ocr",
}


# =========================================================
# BUILD CONVERSATION HISTORY
# =========================================================

def build_history(
    history: list[dict],
) -> str:

    parts: list[str] = []

    for message in history[-8:]:

        if not isinstance(message, dict):
            continue

        role = str(
            message.get(
                "role",
                "user",
            )
            or "user"
        ).strip().upper()

        content = str(
            message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if content:
            parts.append(
                f"{role}: {content}"
            )

    if not parts:
        return "No previous conversation."

    return "\n".join(parts)


# =========================================================
# NORMALIZE STRING
# =========================================================

def safe_string(
    value,
) -> str:

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# EXTRACT ROUTE
# =========================================================

def extract_route(
    output: str,
) -> str:

    output = safe_string(output).lower()

    # -----------------------------------------------------
    # Remove markdown formatting / whitespace
    # -----------------------------------------------------

    output = re.sub(
        r"[^a-z_]",
        "",
        output,
    )

    # -----------------------------------------------------
    # Direct valid route
    # -----------------------------------------------------

    if output in VALID_ROUTES:
        return output

    # -----------------------------------------------------
    # Sometimes an LLM may return additional text.
    #
    # Search for a valid route inside the response.
    # -----------------------------------------------------

    for route in VALID_ROUTES:

        if route in output:
            return route

    # -----------------------------------------------------
    # Safe fallback
    # -----------------------------------------------------

    return "general"


# =========================================================
# SUPERVISOR NODE
# =========================================================

def supervisor_node(
    state: AgentState,
) -> AgentState:

    # =====================================================
    # CURRENT QUERY
    # =====================================================

    query = safe_string(
        state.get(
            "query",
            "",
        )
    )

    # =====================================================
    # SELECTED DOCUMENT
    # =====================================================

    selected_document = safe_string(
        state.get(
            "selected_document",
            "",
        )
    )

    # =====================================================
    # ACTIVE WEB URL
    # =====================================================

    active_web_url = safe_string(
        state.get(
            "active_web_url",
            "",
        )
        or state.get(
            "web_url",
            "",
        )
    )

    # =====================================================
    # DOCUMENT CONTEXT
    # =====================================================

    document_context = state.get(
        "document_context",
        False,
    )

    # Make sure this is a real boolean.
    document_context = bool(
        document_context
    )

    # =====================================================
    # HISTORY
    # =====================================================

    history = state.get(
        "history",
        [],
    )

    if not isinstance(
        history,
        list,
    ):
        history = []

    history_text = build_history(
        history
    )

    # =====================================================
    # BUILD SUPERVISOR PROMPT
    # =====================================================

    try:

        prompt = SUPERVISOR_PROMPT.format(
            selected_document=(
                selected_document
                or "NONE"
            ),

            document_context=(
                str(document_context)
            ),

            active_web_url=(
                active_web_url
                or "NONE"
            ),

            history=history_text,

            query=(
                query
                or "EMPTY"
            ),
        )

    except KeyError as error:

        # -------------------------------------------------
        # If prompts.py does not contain active_web_url
        # or another placeholder, don't crash the API.
        # -------------------------------------------------

        print(
            "[SUPERVISOR PROMPT ERROR]",
            repr(error),
        )

        return {
            **state,
            "route": "general",
            "error": (
                f"Supervisor prompt formatting failed: "
                f"{error}"
            ),
        }

    # =====================================================
    # LOG
    # =====================================================

    print(
        "\n================ SUPERVISOR ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Active URL:",
        active_web_url or "NONE",
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
        "============================================"
    )

    # =====================================================
    # LLM ROUTING
    # =====================================================

    try:

        raw_route = llm.generate(
            prompt
        )

        route = extract_route(
            raw_route
        )

        routing_method = "LLM"

    except Exception as error:

        print(
            "[SUPERVISOR LLM ERROR]",
            repr(error),
        )

        # -------------------------------------------------
        # Safe fallback
        # -------------------------------------------------

        route = "general"

        routing_method = "FALLBACK"

        state = {
            **state,

            "llm_error": str(
                error
            ),
        }

    # =====================================================
    # FINAL ROUTE LOG
    # =====================================================

    print(
        "\n================ SUPERVISOR ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Active URL:",
        active_web_url or "NONE",
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    print(
        "Route:",
        route,
    )

    print(
        "Routing method:",
        routing_method,
    )

    print(
        "============================================\n"
    )

    # =====================================================
    # RETURN STATE
    # =====================================================

    return {
        **state,

        "query": query,

        "selected_document": (
            selected_document
        ),

        "active_web_url": (
            active_web_url
        ),

        "document_context": (
            document_context
        ),

        "history": history,

        "route": route,
    }


# =========================================================
# COMPATIBILITY ALIAS
# =========================================================
#
# graph.py currently imports:
#
# from app.agents.supervisor import supervisor
#
# Therefore expose `supervisor`.
#
# =========================================================

supervisor = supervisor_node


# =========================================================
# ROUTE FROM SUPERVISOR
# =========================================================

def route_from_supervisor(
    state: AgentState,
) -> str:

    route = safe_string(
        state.get(
            "route",
            "general",
        )
    ).lower()

    if route not in VALID_ROUTES:
        return "general"

    return route