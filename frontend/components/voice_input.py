from __future__ import annotations

import hashlib

import streamlit as st

from frontend.utils.api_client import api_client


# =========================================================
# HELPERS
# =========================================================

def _extract_transcript(
    result: dict,
) -> str:

    for key in (
        "text",
        "transcript",
        "transcription",
        "recognized_text",
        "message",
    ):

        value = (
            result.get(
                key,
                "",
            )
            or ""
        )

        value = str(
            value
        ).strip()

        if value:

            return value

    return ""


# =========================================================
# VOICE INPUT
# =========================================================

def render_voice_input():

    st.markdown(
        "## 🎙️ Voice Assistant"
    )

    st.caption(
        "Speak your question and let the Agentic RAG Assistant "
        "listen, understand, answer, and speak back."
    )

    # =====================================================
    # RECORD
    # =====================================================

    audio = st.audio_input(
        "🎤 Click here and start speaking",
        key="voice_recorder",
    )

    if audio is None:

        st.info(
            "🎤 Your microphone is ready. "
            "Record a question to begin."
        )

        return

    # =====================================================
    # READ AUDIO
    # =====================================================

    audio_bytes = audio.getvalue()

    if not audio_bytes:

        st.error(
            "❌ The microphone returned an empty recording."
        )

        return

    # =====================================================
    # UNIQUE RECORDING ID
    # =====================================================

    audio_hash = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    # -----------------------------------------------------
    # Prevent Streamlit reruns from processing the same
    # recording repeatedly.
    # -----------------------------------------------------

    if (
        st.session_state.get(
            "processed_voice_hash"
        )
        == audio_hash
    ):

        return

    st.session_state.processed_voice_hash = (
        audio_hash
    )

    # =====================================================
    # PLAY USER'S ORIGINAL VOICE
    # =====================================================

    st.success(
        "✅ Voice recorded successfully."
    )

    st.markdown(
        "**🔊 Your recording:**"
    )

    st.audio(
        audio_bytes,
        format=(
            getattr(
                audio,
                "type",
                None,
            )
            or "audio/wav"
        ),
    )

    # =====================================================
    # TRANSCRIBE
    # =====================================================

    with st.spinner(
        "🎧 Listening and converting your speech to text..."
    ):

        try:

            result = api_client.transcribe_audio(
                audio
            )

        except Exception as error:

            print(
                "\n========== VOICE STT ERROR =========="
            )

            print(
                repr(error)
            )

            print(
                "=====================================\n"
            )

            st.error(
                "❌ I couldn't understand the recording."
            )

            st.caption(
                f"STT error: {error}"
            )

            return

    # =====================================================
    # VALIDATE RESPONSE
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "❌ Invalid response from speech recognition."
        )

        return

    print(
        "\n========== VOICE STT RESPONSE =========="
    )

    print(
        result
    )

    print(
        "=========================================\n"
    )

    # =====================================================
    # TRANSCRIPT
    # =====================================================

    transcript = _extract_transcript(
        result
    )

    if not transcript:

        st.warning(
            "⚠️ No understandable speech was detected. "
            "Please speak clearly and try again."
        )

        return

    # =====================================================
    # SHOW TRANSCRIPT
    # =====================================================

    st.markdown(
        "**📝 You said:**"
    )

    st.info(
        transcript
    )

    # =====================================================
    # SAVE USER AUDIO
    # =====================================================

    st.session_state.voice_audio = (
        audio_bytes
    )

    st.session_state.voice_transcript = (
        transcript
    )

    # =====================================================
    # IMPORTANT
    #
    # Do NOT add the message and then rerun.
    #
    # We process the COMPLETE voice request here.
    # =====================================================

    if "messages" not in st.session_state:

        st.session_state.messages = []

    # =====================================================
    # HISTORY BEFORE CURRENT VOICE MESSAGE
    # =====================================================

    history = []

    for message in st.session_state.messages:

        if not isinstance(
            message,
            dict,
        ):

            continue

        content = (
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

    # =====================================================
    # ADD USER MESSAGE
    # =====================================================

    user_message = {

        "role": "user",

        "content": transcript,

        "input_type": "voice",

    }

    st.session_state.messages.append(
        user_message
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

    web_url = (
        st.session_state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

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

    # =====================================================
    # SEND TO SAME AGENT AS TEXT CHAT
    # =====================================================

    with st.spinner(
        "🤖 Thinking..."
    ):

        try:

            result = api_client.chat(

                message=transcript,

                selected_document=(
                    selected_document
                ),

                document_context=(
                    document_context
                ),

                web_url=web_url,

                web_context=web_context,

                ocr_text=ocr_text,

                history=history,
            )

        except Exception as error:

            print(
                "\n========== VOICE CHAT ERROR =========="
            )

            print(
                repr(error)
            )

            print(
                "======================================\n"
            )

            st.error(
                f"❌ Assistant failed: {error}"
            )

            return

    # =====================================================
    # ANSWER
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "❌ Assistant returned an invalid response."
        )

        return

    answer = (
        result.get(
            "answer",
            "",
        )
        or ""
    ).strip()

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

    sources = (
        result.get(
            "sources",
            [],
        )
        or []
    )

    backend_web_url = (
        result.get(
            "web_url",
            web_url,
        )
        or web_url
    )

    if not answer:

        answer = (
            "I couldn't generate an answer."
        )

    # =====================================================
    # DISPLAY ASSISTANT TEXT
    # =====================================================

    st.markdown(
        "### 🤖 Assistant"
    )

    st.markdown(
        answer
    )

    st.caption(
        f"Route: {route}"
    )

    if (
        backend_web_url
        and route == "web_rag"
    ):

        st.caption(
            f"🌐 Source webpage: {backend_web_url}"
        )

    # =====================================================
    # GENERATE ASSISTANT VOICE
    # =====================================================

    assistant_audio = None

    with st.spinner(
        "🔊 Preparing spoken response..."
    ):

        try:

            assistant_audio = (
                api_client.text_to_speech(
                    answer
                )
            )

        except Exception as error:

            print(
                "\n========== VOICE TTS ERROR =========="
            )

            print(
                repr(error)
            )

            print(
                "======================================\n"
            )

            st.warning(
                "The answer was generated, "
                "but I couldn't generate the spoken response."
            )

    # =====================================================
    # PLAY ASSISTANT VOICE
    # =====================================================

    if assistant_audio:

        st.markdown(
            "**🔊 Assistant voice:**"
        )

        st.audio(
            assistant_audio,
            format="audio/wav",
        )

    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

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

        "selected_document": (
            selected_document
        ),

        "document_context": (
            document_context
        ),

        "input_type": "assistant",
    }

    if assistant_audio:

        assistant_message["audio"] = (
            assistant_audio
        )

    st.session_state.messages.append(
        assistant_message
    )

    # =====================================================
    # DONE
    # =====================================================

    print(
        "\n========== VOICE CONVERSATION COMPLETE =========="
    )

    print(
        "User:",
        transcript,
    )

    print(
        "Assistant:",
        answer,
    )

    print(
        "Route:",
        route,
    )

    print(
        "TTS:",
        bool(assistant_audio),
    )

    print(
        "===================================================\n"
    )

    # -----------------------------------------------------
    # Rerun ONLY AFTER EVERYTHING HAS COMPLETED.
    #
    # This makes the conversation history render cleanly.
    # -----------------------------------------------------

    st.rerun()