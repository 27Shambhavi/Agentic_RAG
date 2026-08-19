from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import api_client
from frontend.components.sources import render_sources

from app.rag.web_rag import extract_url


ROUTE_LABELS = {
    "rag": "📄 Document RAG",
    "web": "🌐 Web Search",
    "web_rag": "🌐 Web RAG",
    "general": "🤖 General AI",
    "greeting": "👋 Greeting",
    "weather": "🌤️ Weather",
    "ocr": "🖼️ Vision & OCR",
    "error": "❌ Error",
}


def _init_state():

    defaults = {
        "messages": [],
        "selected_document": "",
        "document_context": False,
        "ocr_text": "",
        "web_url": "",
        "web_context": False,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[
                key
            ] = value


def _history():

    history = []

    for message in st.session_state.messages:

        if not isinstance(
            message,
            dict,
        ):
            continue

        content = str(
            message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if content:

            history.append(
                {
                    "role": message.get(
                        "role",
                        "user",
                    ),
                    "content": content,
                }
            )

    return history


def _display_message(
    message: dict,
):

    role = message.get(
        "role",
        "assistant",
    )

    content = (
        message.get(
            "content",
            "",
        )
        or ""
    )

    with st.chat_message(
        role
    ):

        st.markdown(
            content
        )

        route = str(
            message.get(
                "route",
                "",
            )
            or ""
        ).lower()

        if route:

            st.caption(
                "Route: "
                + ROUTE_LABELS.get(
                    route,
                    route.title(),
                )
            )

        web_url = str(
            message.get(
                "web_url",
                "",
            )
            or ""
        ).strip()

        if (
            route == "web_rag"
            and web_url
        ):

            st.caption(
                f"🌐 Webpage: {web_url}"
            )

        sources = (
            message.get(
                "sources",
                [],
            )
            or []
        )

        if sources:

            render_sources(
                sources
            )


def _resolve_web_url(
    query: str,
) -> str:

    # -----------------------------------------------------
    # New URL in current question
    # -----------------------------------------------------

    detected = ""

    try:

        detected = (
            extract_url(
                query
            )
            or ""
        ).strip()

    except Exception:
        detected = ""

    if detected:

        st.session_state.web_url = (
            detected
        )

        st.session_state.web_context = (
            True
        )

        return detected

    # -----------------------------------------------------
    # Otherwise preserve previous URL.
    #
    # Supervisor decides whether it should actually be
    # used. A selected PDF gets priority there.
    # -----------------------------------------------------

    return (
        st.session_state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()


def render_chat():

    _init_state()

    # =====================================================
    # HISTORY
    # =====================================================

    for message in (
        st.session_state.messages
    ):

        _display_message(
            message
        )

    # =====================================================
    # INPUT
    # =====================================================

    prompt = st.chat_input(
        "Ask something...",
        key="main_chat_input",
    )

    if (
        not prompt
        or not prompt.strip()
    ):

        return

    user_query = (
        prompt.strip()
    )

    # =====================================================
    # CURRENT CONTEXT
    # =====================================================

    selected_document = (
        st.session_state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    document_context = bool(
        selected_document
    )

    st.session_state.document_context = (
        document_context
    )

    web_url = _resolve_web_url(
        user_query
    )

    web_context = bool(
        web_url
    )

    ocr_text = (
        st.session_state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    history = _history()

    # =====================================================
    # IMPORTANT:
    #
    # Save and DISPLAY user message BEFORE backend call.
    #
    # This is the normal Streamlit chat pattern.
    # =====================================================

    user_message = {
        "role": "user",

        "content": user_query,

        "input_type": "text",
    }

    st.session_state.messages.append(
        user_message
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_query
        )

    # =====================================================
    # ASSISTANT
    # =====================================================

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Thinking..."
        ):

            try:

                result = api_client.chat(

                    message=user_query,

                    selected_document=(
                        selected_document
                    ),

                    document_context=(
                        document_context
                    ),

                    web_url=(
                        web_url
                    ),

                    web_context=(
                        web_context
                    ),

                    ocr_text=(
                        ocr_text
                    ),

                    history=(
                        history
                    ),
                )

                if not isinstance(
                    result,
                    dict,
                ):

                    raise ValueError(
                        "Invalid backend response."
                    )

                answer = (
                    result.get(
                        "answer",
                        "",
                    )
                    or ""
                ).strip()

                if not answer:

                    answer = (
                        "I couldn't generate an answer."
                    )

                route = str(
                    result.get(
                        "route",
                        "general",
                    )
                    or "general"
                ).strip().lower()

                sources = (
                    result.get(
                        "sources",
                        [],
                    )
                    or []
                )

                backend_web_url = str(
                    result.get(
                        "web_url",
                        "",
                    )
                    or ""
                ).strip()

                # =================================================
                # WEB URL STATE
                # =================================================

                if route == "web_rag":

                    if backend_web_url:

                        st.session_state.web_url = (
                            backend_web_url
                        )

                        st.session_state.web_context = (
                            True
                        )

                elif route == "rag":

                    # IMPORTANT:
                    #
                    # Do NOT delete web_url.
                    #
                    # The old URL can be reused later
                    # after leaving PDF context.
                    #
                    st.session_state.web_context = (
                        False
                    )

                # =================================================
                # DISPLAY
                # =================================================

                st.markdown(
                    answer
                )

                st.caption(
                    "Route: "
                    + ROUTE_LABELS.get(
                        route,
                        route.title(),
                    )
                )

                if (
                    route == "web_rag"
                    and backend_web_url
                ):

                    st.caption(
                        f"🌐 Webpage: {backend_web_url}"
                    )

                if sources:

                    render_sources(
                        sources
                    )

                # =================================================
                # SAVE ASSISTANT
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content": answer,

                        "route": route,

                        "sources": sources,

                        "web_url": (
                            backend_web_url
                            if route == "web_rag"
                            else ""
                        ),

                        "selected_document": (
                            selected_document
                        ),

                        "document_context": (
                            document_context
                        ),

                        "input_type": "assistant",
                    }
                )

            except Exception as error:

                print(
                    "[CHAT ERROR]",
                    repr(error),
                )

                answer = (
                    f"Backend error: {error}"
                )

                st.error(
                    answer
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content": answer,

                        "route": "error",

                        "sources": [],

                        "web_url": "",

                        "input_type": "assistant",
                    }
                )