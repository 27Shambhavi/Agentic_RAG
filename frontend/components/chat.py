import streamlit as st

from frontend.utils.api_client import api_client
from frontend.components.sources import render_sources


# =========================================================
# ROUTE LABELS
# =========================================================

ROUTE_LABELS = {
    "rag": "📄 Document RAG",
    "web": "🌐 Web Search",
    "general": "🤖 General AI",
    "greeting": "👋 Greeting",
    "weather": "🌤️ Weather",
    "ocr": "🖼️ Vision & OCR",
    "error": "❌ Error",
}


# =========================================================
# CHAT
# =========================================================

def render_chat():

    st.markdown(
        "### 💬 Conversation"
    )

    st.caption(
        "Ask anything. Your conversation stays here."
    )

    # =====================================================
    # INITIALIZE SESSION STATE
    # =====================================================

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_document" not in st.session_state:
        st.session_state.selected_document = ""

    if "document_context" not in st.session_state:
        st.session_state.document_context = False

    if "ocr_text" not in st.session_state:
        st.session_state.ocr_text = ""

    # =====================================================
    # DISPLAY EXISTING MESSAGES
    # =====================================================

    if not st.session_state.messages:

        st.info(
            "👋 Start a conversation by asking a question below."
        )

    else:

        for message in st.session_state.messages:

            role = message.get(
                "role",
                "assistant",
            )

            content = message.get(
                "content",
                "",
            )

            with st.chat_message(role):

                st.markdown(
                    content
                )

                # -----------------------------------------
                # ROUTE
                # -----------------------------------------

                route = message.get(
                    "route",
                    "",
                )

                if route:

                    route = (
                        str(route)
                        .strip()
                        .lower()
                    )

                    label = ROUTE_LABELS.get(
                        route,
                        route.title(),
                    )

                    st.caption(
                        f"Route: {label}"
                    )

                # -----------------------------------------
                # SOURCES
                # -----------------------------------------

                sources = message.get(
                    "sources",
                    [],
                ) or []

                if sources:

                    render_sources(
                        sources
                    )

    # =====================================================
    # CHAT INPUT
    # =====================================================

    prompt = st.chat_input(
        "Ask something..."
    )

    if not prompt or not prompt.strip():
        return

    user_query = prompt.strip()

    # =====================================================
    # CURRENT DOCUMENT
    # =====================================================

    selected_document = (
        st.session_state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # DOCUMENT MODE
    #
    # If a document is selected, this conversation is
    # document-aware.
    # =====================================================

    document_context = bool(
        selected_document
    )

    # =====================================================
    # FORCE RAG
    #
    # IMPORTANT:
    #
    # Selected PDF -> RAG
    #
    # This prevents the supervisor from sending a normal
    # document question to web search.
    #
    # Explicit web requests can still be handled separately
    # by the backend if you later decide to support them.
    # =====================================================

    force_rag = bool(
        selected_document
    )

    # =====================================================
    # KEEP SESSION STATE SYNCHRONIZED
    # =====================================================

    st.session_state.document_context = (
        document_context
    )

    # =====================================================
    # OCR
    # =====================================================

    ocr_text = (
        st.session_state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # BUILD HISTORY
    #
    # Current user message is NOT included.
    # =====================================================

    history = []

    for message in st.session_state.messages:

        history.append(
            {
                "role": message.get(
                    "role",
                    "user",
                ),
                "content": message.get(
                    "content",
                    "",
                ),
            }
        )

    # =====================================================
    # ADD USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    # =====================================================
    # ASSISTANT RESPONSE
    # =====================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                # =========================================
                # FRONTEND DEBUG
                # =========================================

                print(
                    "\n========== FRONTEND CHAT =========="
                )

                print(
                    "User:",
                    user_query,
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
                    "Force RAG:",
                    force_rag,
                )

                print(
                    "History messages:",
                    len(history),
                )

                # =========================================
                # CALL BACKEND
                # =========================================

                result = api_client.chat(
                    message=user_query,

                    selected_document=(
                        selected_document
                    ),

                    document_context=(
                        document_context
                    ),

                    force_rag=(
                        force_rag
                    ),

                    ocr_text=(
                        ocr_text
                    ),

                    history=(
                        history
                    ),
                )

                # =========================================
                # DEBUG BACKEND RESPONSE
                # =========================================

                print(
                    "Backend result:",
                    result,
                )

                print(
                    "===================================\n"
                )

                # =========================================
                # VALIDATE RESPONSE
                # =========================================

                if not isinstance(
                    result,
                    dict,
                ):

                    raise ValueError(
                        "Backend returned an invalid response."
                    )

                # =========================================
                # ANSWER
                # =========================================

                answer = (
                    result.get(
                        "answer",
                        "",
                    )
                    or ""
                ).strip()

                # =========================================
                # ROUTE
                # =========================================

                route = (
                    result.get(
                        "route",
                        "general",
                    )
                    or "general"
                )

                route = (
                    str(route)
                    .strip()
                    .lower()
                )

                # =========================================
                # SOURCES
                # =========================================

                sources = (
                    result.get(
                        "sources",
                        [],
                    )
                    or []
                )

                # =========================================
                # IMPORTANT
                #
                # DO NOT CHANGE WEB -> RAG HERE.
                #
                # The frontend must display the actual
                # backend route.
                #
                # If backend says WEB, we need to see WEB
                # so we can fix the backend routing.
                # =========================================

                # =========================================
                # EMPTY ANSWER
                # =========================================

                if not answer:

                    answer = (
                        "The backend returned no answer."
                    )

                # =========================================
                # DISPLAY ANSWER
                # =========================================

                st.markdown(
                    answer
                )

                # =========================================
                # DISPLAY ROUTE
                # =========================================

                label = ROUTE_LABELS.get(
                    route,
                    route.title(),
                )

                st.caption(
                    f"Route: {label}"
                )

                # =========================================
                # DISPLAY SOURCES
                # =========================================

                if sources:

                    render_sources(
                        sources
                    )

                # =========================================
                # SAVE ASSISTANT MESSAGE
                # =========================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content": answer,

                        "route": route,

                        "sources": sources,

                        "selected_document": (
                            selected_document
                        ),

                        "document_context": (
                            document_context
                        ),
                    }
                )

            # =================================================
            # FRONTEND ERROR
            # =================================================

            except Exception as error:

                print(
                    "\n========== FRONTEND CHAT ERROR =========="
                )

                print(
                    repr(error)
                )

                print(
                    "=========================================\n"
                )

                error_message = (
                    f"Backend error: {error}"
                )

                st.error(
                    error_message
                )

                # =========================================
                # SAVE ERROR
                # =========================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content": error_message,

                        "route": "error",

                        "sources": [],
                    }
                )