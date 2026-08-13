from app.agents.state import AgentState
from app.agents.classifier import classify_intent

from app.rag.document_rag import document_rag
from app.llm.gemini import llm


# =========================================================
# SUPERVISOR NODE
# =========================================================

def supervisor_node(
    state: AgentState,
) -> AgentState:

    query = state.get(
        "query",
        "",
    ).strip()

    selected_document = state.get(
        "selected_document",
        "",
    ).strip()

    document_context = state.get(
        "document_context",
        False,
    )


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
    # CLASSIFY USER INTENT
    # =====================================================
    #
    # IMPORTANT:
    #
    # Do NOT do:
    #
    # if selected_document:
    #     route = "rag"
    #
    # because then:
    #
    # "What is iPhone 17 price?"
    #
    # would incorrectly go to PDF RAG.
    #
    # The classifier decides based on the actual question.
    #


    try:

        route = classify_intent(
            query
        )

    except Exception as error:

        print(
            "[CLASSIFIER ERROR]",
            repr(error),
        )

        route = "general"


    # =====================================================
    # VALID ROUTES
    # =====================================================

    valid_routes = {
        "rag",
        "web",
        "general",
        "greeting",
    }

    if route not in valid_routes:

        route = "general"


    # =====================================================
    # DOCUMENT FOLLOW-UP HANDLING
    # =====================================================
    #
    # document_context can be used for short follow-up
    # questions such as:
    #
    # User:
    #   What are the benefits of PM-JAY?
    #
    # Assistant:
    #   ...
    #
    # User:
    #   What about eligibility?
    #
    # If classifier identifies the second question as RAG,
    # the active document is passed to rag_node.
    #
    # We DO NOT force RAG merely because a document exists.
    #


    return {
        **state,

        "route": route,

        # Preserve these values explicitly
        # for downstream nodes.
        "selected_document": selected_document,
        "document_context": document_context,
    }


# =========================================================
# DOCUMENT RAG NODE
# =========================================================

def rag_node(
    state: AgentState,
) -> AgentState:

    query = state.get(
        "query",
        "",
    ).strip()

    selected_document = state.get(
        "selected_document",
        "",
    ).strip()


    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,
            "answer": "",
            "sources": [],
        }


    # =====================================================
    # NO ACTIVE DOCUMENT
    # =====================================================

    if not selected_document:

        return {
            **state,

            "answer": (
                "Please upload and select a document "
                "before asking a document-based question."
            ),

            "sources": [],
        }


    # =====================================================
    # DOCUMENT RAG
    # =====================================================

    try:

        result = document_rag(
            query=query,
            selected_document=selected_document,
        )


        # -------------------------------------------------
        # SAFETY
        # -------------------------------------------------

        if not isinstance(
            result,
            dict,
        ):

            return {
                **state,

                "answer": str(
                    result
                ),

                "sources": [],
            }


        return {
            **state,

            "answer": result.get(
                "answer",
                "",
            ),

            "sources": result.get(
                "sources",
                [],
            ),

            "selected_document": (
                selected_document
            ),

            "document_context": True,
        }


    except Exception as error:

        print(
            "[RAG ERROR]",
            repr(error),
        )

        return {
            **state,

            "answer": (
                "I couldn't retrieve information "
                "from the active document."
            ),

            "sources": [],
        }


# =========================================================
# GENERAL AI NODE
# =========================================================

def general_node(
    state: AgentState,
) -> AgentState:

    query = state.get(
        "query",
        "",
    ).strip()


    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,
            "answer": "",
            "sources": [],
        }


    # =====================================================
    # GENERAL AI PROMPT
    # =====================================================

    prompt = f"""
You are a helpful general AI assistant.

Answer the user's question naturally, clearly,
and directly.

IMPORTANT RULES:

1. This is a general AI question.
2. Do NOT use uploaded PDF information.
3. Do NOT use document context.
4. Do NOT mention RAG.
5. Do NOT create document citations.
6. Do NOT pretend the answer came from a PDF.
7. If current information is required, that should
   be handled by the web-search route.
8. Do not invent information.

USER QUESTION:

{query}

ANSWER:
"""


    # =====================================================
    # GENERATE
    # =====================================================

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[GENERAL AI ERROR]",
            repr(error),
        )

        answer = (
            "Sorry, I couldn't generate "
            "an answer right now."
        )


    return {
        **state,

        "answer": answer,

        # General answers never have PDF sources.
        "sources": [],
    }


# =========================================================
# GREETING NODE
# =========================================================

def greeting_node(
    state: AgentState,
) -> AgentState:

    return {
        **state,

        "answer": (
            "Hello! 👋 How can I help you today?"
        ),

        "sources": [],
    }


# =========================================================
# WEB SEARCH NODE
# =========================================================

def web_node(
    state: AgentState,
) -> AgentState:

    query = state.get(
        "query",
        "",
    ).strip()


    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,
            "answer": "",
            "sources": [],
        }


    # =====================================================
    # DUCKDUCKGO / DDGS WEB SEARCH
    # =====================================================

    try:

        from app.tools.web_search_tool import (
            web_search,
        )


        result = web_search(
            query=query,
            max_results=5,
        )


        # -------------------------------------------------
        # EXPECTED RESULT
        #
        # {
        #     "answer": "...",
        #     "sources": [...]
        # }
        # -------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            answer = result.get(
                "answer",
                "",
            )

            sources = result.get(
                "sources",
                [],
            )


        # -------------------------------------------------
        # FALLBACK IF TOOL RETURNS STRING
        # -------------------------------------------------

        else:

            answer = str(
                result
            )

            sources = []


        return {
            **state,

            "answer": answer,

            "sources": sources,
        }


    except Exception as error:

        print(
            "[WEB SEARCH ERROR]",
            repr(error),
        )

        return {
            **state,

            "answer": (
                "I couldn't perform the web search "
                "right now."
            ),

            "sources": [],
        }


# =========================================================
# ROUTE EXECUTION
# =========================================================

def route_node(
    state: AgentState,
) -> AgentState:

    route = state.get(
        "route",
        "general",
    )


    # =====================================================
    # DOCUMENT RAG
    # =====================================================

    if route == "rag":

        return rag_node(
            state
        )


    # =====================================================
    # WEB SEARCH
    # =====================================================

    if route == "web":

        return web_node(
            state
        )


    # =====================================================
    # GREETING
    # =====================================================

    if route == "greeting":

        return greeting_node(
            state
        )


    # =====================================================
    # GENERAL AI
    # =====================================================

    return general_node(
        state
    )