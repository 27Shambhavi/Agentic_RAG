from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import api_client
from frontend.components.sources import render_sources
from app.rag.web_rag import extract_url


# =========================================================
# ROUTE LABELS
# =========================================================

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


# =========================================================
# SESSION STATE
# =========================================================

def _initialize_state() -> None:

    defaults = {
        "messages": [],
        "selected_document": "",
        "document_context": False,

        "ocr_text": "",

        # Active Web RAG URL
        "web_url": "",
        "web_context": False,

        # Voice
        "voice_response_requested": False,
        "voice_audio": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# =========================================================
# HISTORY
# =========================================================

def _build_history() -> list[dict]:

    messages = st.session_state.messages

    if not messages:

        return []

    history = []

    # -----------------------------------------------------
    # Exclude newest message.
    #
    # The newest message is the current request.
    # -----------------------------------------------------

    for message in messages[:-1]:

        if not isinstance(message, dict):

            continue

        content = str(
            message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if not content:

            continue

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


# =========================================================
# DISPLAY MESSAGE
# =========================================================

def _display_message(
    message: dict,
) -> None:

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
    ).strip()

    with st.chat_message(role):

        # -------------------------------------------------
        # CONTENT
        # -------------------------------------------------

        if content:

            st.markdown(
                content
            )

        # -------------------------------------------------
        # VOICE USER MESSAGE
        # -------------------------------------------------

        if (
            role == "user"
            and message.get(
                "input_type",
                "",
            ) == "voice"
        ):

            st.caption(
                "🎙️ Voice message"
            )

        # -------------------------------------------------
        # ROUTE
        # -------------------------------------------------

        route = (
            message.get(
                "route",
                "",
            )
            or ""
        )

        route = str(
            route
        ).strip().lower()

        if route:

            label = ROUTE_LABELS.get(
                route,
                route.title(),
            )

            st.caption(
                f"Route: {label}"
            )

        # -------------------------------------------------
        # WEB RAG URL
        # -------------------------------------------------

        message_web_url = (
            message.get(
                "web_url",
                "",
            )
            or ""
        ).strip()

        if message_web_url:

            st.caption(
                f"🌐 Webpage: {message_web_url}"
            )

        # -------------------------------------------------
        # SOURCES
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ASSISTANT AUDIO
        # -------------------------------------------------

        audio_data = message.get(
            "audio",
            None,
        )

        if audio_data:

            try:

                st.audio(
                    audio_data,
                    format="audio/wav",
                )

            except Exception as error:

                print(
                    "[CHAT] AUDIO DISPLAY ERROR:",
                    repr(error),
                )


# =========================================================
# PENDING VOICE MESSAGE
# =========================================================

def _get_pending_voice_message():

    requested = bool(
        st.session_state.get(
            "voice_response_requested",
            False,
        )
    )

    if not requested:

        return None

    messages = st.session_state.messages

    if not messages:

        return None

    latest = messages[-1]

    if not isinstance(
        latest,
        dict,
    ):

        return None

    if (
        latest.get("role") == "user"
        and latest.get("input_type") == "voice"
    ):

        return latest

    return None


# =========================================================
# WEB URL RESOLUTION
# =========================================================
#
# ROUTING RULES
#
# ---------------------------------------------------------
#
# 1. URL in CURRENT user message
#       ↓
#    WEB RAG
#
# ---------------------------------------------------------
#
# 2. No URL + PDF selected
#       ↓
#    CLEAR OLD WEB URL
#       ↓
#    PDF RAG
#
# ---------------------------------------------------------
#
# 3. No URL + no PDF + previous Web RAG URL
#       ↓
#    REUSE URL
#       ↓
#    WEB RAG follow-up
#
# ---------------------------------------------------------
#
# This prevents:
#
# Magicbricks URL
#       ↓
# new PDF selected
#       ↓
# old Magicbricks URL
#       ↓
# WRONG WEB SEARCH
#
# =========================================================

def _resolve_web_url(
    user_query: str,
    selected_document: str = "",
) -> str:

    user_query = (
        user_query or ""
    ).strip()

    selected_document = (
        selected_document or ""
    ).strip()

    # =====================================================
    # 1. DETECT URL IN CURRENT QUERY
    # =====================================================

    detected_url = ""

    try:

        detected_url = (
            extract_url(
                user_query
            )
            or ""
        ).strip()

    except Exception as error:

        print(
            "[WEB URL EXTRACTION ERROR]",
            repr(error),
        )

        detected_url = ""

    # =====================================================
    # EXPLICIT CURRENT URL
    # =====================================================
    #
    # CURRENT URL HAS HIGHEST PRIORITY.
    #
    # Example:
    #
    # https://www.magicbricks.com/
    # what services does this provide?
    #
    # -> WEB RAG
    #
    # =====================================================

    if detected_url:

        print(
            "\n[WEB] =================================="
        )

        print(
            "[WEB] Explicit URL detected."
        )

        print(
            "[WEB] URL:",
            detected_url,
        )

        print(
            "[WEB] Route should be WEB RAG."
        )

        print(
            "[WEB] ==================================\n"
        )

        st.session_state.web_url = (
            detected_url
        )

        st.session_state.web_context = True

        return detected_url

    # =====================================================
    # 2. ACTIVE PDF
    # =====================================================
    #
    # NO NEW URL + PDF SELECTED
    #
    # Clear any stale Web RAG URL.
    #
    # =====================================================

    if selected_document:

        old_url = (
            st.session_state.get(
                "web_url",
                "",
            )
            or ""
        ).strip()

        if old_url:

            print(
                "\n[WEB] =================================="
            )

            print(
                "[WEB] Active PDF detected."
            )

            print(
                "[WEB] Clearing stale Web URL:",
                old_url,
            )

            print(
                "[WEB] PDF RAG will handle this request."
            )

            print(
                "[WEB] ==================================\n"
            )

        # -------------------------------------------------
        # CRITICAL
        # -------------------------------------------------
        #
        # Do NOT send the previous URL to backend.
        #
        # -------------------------------------------------

        st.session_state.web_url = ""

        st.session_state.web_context = False

        return ""

    # =====================================================
    # 3. NO PDF
    #
    # REUSE PREVIOUS WEB RAG URL
    # =====================================================

    current_url = (
        st.session_state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

    if current_url:

        print(
            "\n[WEB] =================================="
        )

        print(
            "[WEB] Reusing previous Web RAG URL:"
        )

        print(
            current_url
        )

        print(
            "[WEB] ==================================\n"
        )

        st.session_state.web_url = (
            current_url
        )

        st.session_state.web_context = True

        return current_url

    # =====================================================
    # 4. NO URL
    # =====================================================

    st.session_state.web_url = ""

    st.session_state.web_context = False

    print(
        "[WEB] No active Web RAG URL."
    )

    return ""


# =========================================================
# BACKEND REQUEST
# =========================================================

def _send_request(
    user_query: str,
    input_type: str,
    history: list[dict],
    selected_document: str,
    document_context: bool,
    web_url: str,
    web_context: bool,
    ocr_text: str,
) -> None:

    with st.chat_message(
        "assistant"
    ):

        spinner_text = (
            "🎙️ Thinking and preparing voice response..."
            if input_type == "voice"
            else "Thinking..."
        )

        with st.spinner(
            spinner_text
        ):

            try:

                print(
                    "\n========== FRONTEND CHAT =========="
                )

                print(
                    "User:",
                    user_query,
                )

                print(
                    "Input type:",
                    input_type,
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
                    "Web URL:",
                    web_url or "NONE",
                )

                print(
                    "Web context:",
                    web_context,
                )

                print(
                    "OCR available:",
                    bool(ocr_text),
                )

                print(
                    "History messages:",
                    len(history),
                )

                # =================================================
                # BACKEND CALL
                # =================================================

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

                print(
                    "Backend result:",
                    result,
                )

                # =================================================
                # VALIDATE RESPONSE
                # =================================================

                if not isinstance(
                    result,
                    dict,
                ):

                    raise ValueError(
                        "Backend returned an invalid response."
                    )

                # =================================================
                # ANSWER
                # =================================================

                answer = (
                    result.get(
                        "answer",
                        "",
                    )
                    or ""
                ).strip()

                if not answer:

                    answer = (
                        "The backend returned no answer."
                    )

                # =================================================
                # ROUTE
                # =================================================

                route = (
                    result.get(
                        "route",
                        "general",
                    )
                    or "general"
                )

                route = str(
                    route
                ).strip().lower()

                # =================================================
                # SOURCES
                # =================================================

                sources = (
                    result.get(
                        "sources",
                        [],
                    )
                    or []
                )

                # =================================================
                # BACKEND WEB URL
                # =================================================

                backend_web_url = (
                    result.get(
                        "web_url",
                        "",
                    )
                    or ""
                ).strip()

                # =================================================
                # WEB RAG STATE MANAGEMENT
                # =================================================
                #
                # IMPORTANT:
                #
                # Only Web RAG can keep a Web URL alive.
                #
                # PDF RAG clears it.
                #
                # =================================================

                if route == "web_rag":

                    # Backend URL is authoritative.
                    if backend_web_url:

                        st.session_state.web_url = (
                            backend_web_url
                        )

                        st.session_state.web_context = True

                    # Fallback to URL we sent.
                    elif web_url:

                        st.session_state.web_url = (
                            web_url
                        )

                        st.session_state.web_context = True

                elif route == "rag":

                    # -------------------------------------------------
                    # PDF RAG WON
                    # -------------------------------------------------
                    #
                    # Absolutely do not preserve old Web RAG URL.
                    #
                    # -------------------------------------------------

                    st.session_state.web_url = ""

                    st.session_state.web_context = False

                # =================================================
                # DISPLAY ANSWER
                # =================================================

                st.markdown(
                    answer
                )

                # =================================================
                # DISPLAY ROUTE
                # =================================================

                label = ROUTE_LABELS.get(
                    route,
                    route.title(),
                )

                st.caption(
                    f"Route: {label}"
                )

                # =================================================
                # DISPLAY WEB RAG URL
                # =================================================

                if (
                    route == "web_rag"
                    and backend_web_url
                ):

                    st.caption(
                        f"🌐 Source webpage: {backend_web_url}"
                    )

                # =================================================
                # SOURCES
                # =================================================

                if sources:

                    render_sources(
                        sources
                    )

                # =================================================
                # VOICE RESPONSE
                # =================================================

                audio_data = None

                if input_type == "voice":

                    print(
                        "[VOICE] Generating assistant speech..."
                    )

                    try:

                        audio_data = (
                            api_client.text_to_speech(
                                answer
                            )
                        )

                        if audio_data:

                            st.audio(
                                audio_data,
                                format="audio/wav",
                            )

                            print(
                                "[VOICE] TTS generated successfully."
                            )

                        else:

                            print(
                                "[VOICE] TTS returned empty audio."
                            )

                    except Exception as error:

                        print(
                            "[VOICE TTS ERROR]",
                            repr(error),
                        )

                        st.warning(
                            "🔊 The answer was generated, "
                            "but the voice response could not "
                            "be generated."
                        )

                # =================================================
                # SAVE ASSISTANT MESSAGE
                # =================================================

                assistant_message = {

                    "role": "assistant",

                    "content": answer,

                    "route": route,

                    "sources": sources,

                    # Only Web RAG messages retain URL.
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

                if audio_data:

                    assistant_message[
                        "audio"
                    ] = audio_data

                st.session_state.messages.append(
                    assistant_message
                )

                # =================================================
                # RESET VOICE FLAG
                # =================================================

                st.session_state.voice_response_requested = (
                    False
                )

                print(
                    "[CHAT] Request completed."
                )

                print(
                    "====================================\n"
                )

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

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "content": error_message,

                        "route": "error",

                        "sources": [],

                        "web_url": "",

                        "input_type": "assistant",
                    }
                )

                st.session_state.voice_response_requested = (
                    False
                )


# =========================================================
# CHAT
# =========================================================

def render_chat() -> None:

    _initialize_state()

    # =====================================================
    # DISPLAY EXISTING MESSAGES
    # =====================================================

    if not st.session_state.messages:

        st.markdown(
            '<div class="chat-empty-state">'
            '<div class="chat-empty-icon">💬</div>'
            '<div class="chat-empty-title">'
            'Start a conversation'
            '</div>'
            '<div class="chat-empty-text">'
            'Ask a question about your documents, a webpage, '
            'an image, or anything else.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        for message in (
            st.session_state.messages
        ):

            _display_message(
                message
            )

    # =====================================================
    # PENDING VOICE
    # =====================================================

    pending_voice_message = (
        _get_pending_voice_message()
    )

    # =====================================================
    # TEXT INPUT
    # =====================================================

    prompt = None

    if pending_voice_message is None:

        prompt = st.chat_input(
            "Ask something..."
        )

    # =====================================================
    # DETERMINE REQUEST
    # =====================================================

    if pending_voice_message is not None:

        user_query = (
            pending_voice_message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        input_type = "voice"

    else:

        if (
            not prompt
            or not prompt.strip()
        ):

            return

        user_query = (
            prompt.strip()
        )

        input_type = "text"

        # -------------------------------------------------
        # Save user message
        # -------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",

                "content": user_query,

                "input_type": "text",
            }
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    if not user_query:

        st.session_state.voice_response_requested = (
            False
        )

        return

    # =====================================================
    # CURRENT PDF
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

    # =====================================================
    # WEB URL
    # =====================================================
    #
    # IMPORTANT:
    #
    # selected_document is passed here.
    #
    # Therefore:
    #
    # OLD MAGICBRICKS URL
    #       +
    # NEW PDF
    #
    # becomes:
    #
    # web_url = ""
    #
    # and PDF RAG wins.
    #
    # =====================================================

    web_url = _resolve_web_url(
        user_query=user_query,

        selected_document=(
            selected_document
        ),
    )

    web_context = bool(
        web_url
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
    # HISTORY
    # =====================================================

    history = _build_history()

    # =====================================================
    # DEBUG FINAL REQUEST
    # =====================================================

    print(
        "\n========== FINAL FRONTEND STATE =========="
    )

    print(
        "Query:",
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
        "Web URL:",
        web_url or "NONE",
    )

    print(
        "Web context:",
        web_context,
    )

    print(
        "OCR:",
        bool(ocr_text),
    )

    print(
        "===========================================\n"
    )

    # =====================================================
    # SEND REQUEST
    # =====================================================

    _send_request(
        user_query=user_query,

        input_type=input_type,

        history=history,

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
    )