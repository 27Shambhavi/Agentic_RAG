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
        "web_url": "",
        "web_context": False,
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

    # Exclude the newest message because it is the current
    # request being sent to the backend.
    for message in messages[:-1]:

        if not isinstance(message, dict):
            continue

        content = str(
            message.get("content", "")
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

def _display_message(message: dict) -> None:

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

        if content:
            st.markdown(content)

        # Voice user message
        if (
            role == "user"
            and message.get(
                "input_type",
                "",
            ) == "voice"
        ):
            st.caption("🎙️ Voice message")

        # Route
        route = (
            message.get(
                "route",
                "",
            )
            or ""
        )

        route = str(route).strip().lower()

        if route:

            label = ROUTE_LABELS.get(
                route,
                route.title(),
            )

            st.caption(
                f"Route: {label}"
            )

        # Web URL
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

        # Sources
        sources = (
            message.get(
                "sources",
                [],
            )
            or []
        )

        if sources:
            render_sources(sources)

        # Assistant audio
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

    if not isinstance(latest, dict):
        return None

    if (
        latest.get("role") == "user"
        and latest.get("input_type") == "voice"
    ):
        return latest

    return None


# =========================================================
# WEB URL
# =========================================================

def _resolve_web_url(
    user_query: str,
) -> str:

    current_url = ""

    try:

        detected_url = (
            extract_url(user_query)
            or ""
        ).strip()

        if detected_url:

            current_url = detected_url

            st.session_state.web_url = (
                detected_url
            )

            st.session_state.web_context = True

            print(
                "[WEB] New URL detected:",
                detected_url,
            )

        else:

            current_url = (
                st.session_state.get(
                    "web_url",
                    "",
                )
                or ""
            ).strip()

            if current_url:

                print(
                    "[WEB] Reusing saved URL:",
                    current_url,
                )

    except Exception as error:

        print(
            "[WEB URL DETECTION ERROR]",
            repr(error),
        )

        current_url = (
            st.session_state.get(
                "web_url",
                "",
            )
            or ""
        ).strip()

    st.session_state.web_url = current_url
    st.session_state.web_context = bool(
        current_url
    )

    return current_url


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

    with st.chat_message("assistant"):

        spinner_text = (
            "🎙️ Thinking and preparing voice response..."
            if input_type == "voice"
            else "Thinking..."
        )

        with st.spinner(spinner_text):

            try:

                print(
                    "\n========== FRONTEND CHAT =========="
                )

                print("User:", user_query)
                print("Input type:", input_type)
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

                # =========================================
                # BACKEND CALL
                # =========================================

                result = api_client.chat(
                    message=user_query,
                    selected_document=selected_document,
                    document_context=document_context,
                    web_url=web_url,
                    web_context=web_context,
                    ocr_text=ocr_text,
                    history=history,
                )

                print(
                    "Backend result:",
                    result,
                )

                if not isinstance(result, dict):

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

                if not answer:

                    answer = (
                        "The backend returned no answer."
                    )

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

                route = str(
                    route
                ).strip().lower()

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
                # WEB URL
                # =========================================

                backend_web_url = (
                    result.get(
                        "web_url",
                        web_url,
                    )
                    or web_url
                )

                backend_web_url = str(
                    backend_web_url
                ).strip()

                if backend_web_url:

                    st.session_state.web_url = (
                        backend_web_url
                    )

                    st.session_state.web_context = True

                # =========================================
                # DISPLAY ANSWER
                # =========================================

                st.markdown(answer)

                label = ROUTE_LABELS.get(
                    route,
                    route.title(),
                )

                st.caption(
                    f"Route: {label}"
                )

                if (
                    backend_web_url
                    and route == "web_rag"
                ):

                    st.caption(
                        f"🌐 Source webpage: {backend_web_url}"
                    )

                if sources:
                    render_sources(sources)

                # =========================================
                # VOICE RESPONSE
                # =========================================

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

                # =========================================
                # SAVE ASSISTANT MESSAGE
                # =========================================

                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "route": route,
                    "sources": sources,
                    "web_url": (
                        backend_web_url
                        if route == "web_rag"
                        else ""
                    ),
                    "selected_document": selected_document,
                    "document_context": document_context,
                    "input_type": "assistant",
                }

                if audio_data:
                    assistant_message["audio"] = audio_data

                st.session_state.messages.append(
                    assistant_message
                )

                st.session_state.voice_response_requested = (
                    False
                )

                print(
                    "[CHAT] Request completed."
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

                st.error(error_message)

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
            '<div class="chat-empty-title">Start a conversation</div>'
            '<div class="chat-empty-text">'
            'Ask a question about your documents, a webpage, '
            'an image, or anything else.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        for message in st.session_state.messages:
            _display_message(message)

    # =====================================================
    # PENDING VOICE
    # =====================================================

    pending_voice_message = (
        _get_pending_voice_message()
    )

    # =====================================================
    # NORMAL TEXT INPUT
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

        if not prompt or not prompt.strip():
            return

        user_query = prompt.strip()
        input_type = "text"

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

        st.session_state.voice_response_requested = False
        return

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

    document_context = bool(
        selected_document
    )

    st.session_state.document_context = (
        document_context
    )

    # =====================================================
    # WEB URL
    # =====================================================

    web_url = _resolve_web_url(
        user_query
    )

    web_context = bool(web_url)

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
    # REQUEST
    # =====================================================

    _send_request(
        user_query=user_query,
        input_type=input_type,
        history=history,
        selected_document=selected_document,
        document_context=document_context,
        web_url=web_url,
        web_context=web_context,
        ocr_text=ocr_text,
    )
