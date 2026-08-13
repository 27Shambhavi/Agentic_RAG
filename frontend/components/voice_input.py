import streamlit as st

from frontend.utils.api_client import api_client


# =========================================================
# VOICE INPUT
# =========================================================

def render_voice_input():

    # -----------------------------------------------------
    # COMPACT VOICE AREA
    # -----------------------------------------------------

    st.markdown(
        '<div class="voice-input-title">🎙️ Voice input</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Speak naturally. Your voice will become a normal chat message."
    )

    # -----------------------------------------------------
    # AUDIO INPUT
    # -----------------------------------------------------

    audio_file = st.audio_input(
        "Record your question",
        key="voice_recorder",
    )

    if audio_file is None:
        return

    # -----------------------------------------------------
    # PROCESS BUTTON
    # -----------------------------------------------------

    if st.button(
        "✨ Send voice message",
        type="primary",
        use_container_width=True,
        key="send_voice_message",
    ):

        with st.spinner("🎙️ Transcribing..."):

            try:

                # -----------------------------------------
                # TRANSCRIBE
                # -----------------------------------------

                result = api_client.transcribe_audio(
                    audio_file
                )

                transcript = (
                    result.get("text")
                    or result.get("transcription")
                    or result.get("transcript")
                    or ""
                ).strip()

                if not transcript:

                    st.error(
                        "Could not understand the audio."
                    )

                    return

                # -----------------------------------------
                # SAVE AS NORMAL USER MESSAGE
                # -----------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": transcript,
                        "source": "voice",
                    }
                )

                # -----------------------------------------
                # SEND TO SAME CHAT PIPELINE
                # -----------------------------------------

                selected_document = st.session_state.get(
                    "selected_document",
                    "",
                )

                document_context = st.session_state.get(
                    "document_context",
                    False,
                )

                with st.spinner("🤔 Thinking..."):

                    response = api_client.chat(
                        transcript,
                        selected_document=selected_document,
                        document_context=document_context,
                    )

                answer = response.get(
                    "answer",
                    "",
                )

                route = response.get(
                    "route",
                    "general",
                )

                sources = response.get(
                    "sources",
                    [],
                )

                if not answer:

                    answer = (
                        "Sorry, I couldn't generate an answer."
                    )

                # -----------------------------------------
                # SAVE ASSISTANT RESPONSE
                # -----------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "route": route,
                        "sources": sources,
                        "source": "voice",
                    }
                )

                # -----------------------------------------
                # RETURN TO NORMAL CONVERSATION
                # -----------------------------------------

                st.session_state.active_tool = (
                    "conversation"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Voice processing failed: {error}"
                )