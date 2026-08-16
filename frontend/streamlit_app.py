from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent.parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# =========================================================
# FRONTEND IMPORTS
# =========================================================

from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat
from frontend.components.document_upload import render_document_upload
from frontend.components.document_library import render_document_library
from frontend.components.image_upload import render_image_upload


# =========================================================
# OPTIONAL VOICE COMPONENT
# =========================================================

try:

    from frontend.components.voice_input import render_voice_input

    VOICE_COMPONENT_AVAILABLE = True

except ImportError:

    VOICE_COMPONENT_AVAILABLE = False
    render_voice_input = None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css() -> None:

    candidates = [
        PROJECT_ROOT / "frontend" / "style.css",
        PROJECT_ROOT / "frontend" / "styles.css",
        PROJECT_ROOT / "frontend" / "components" / "style.css",
    ]

    for css_file in candidates:

        if css_file.exists():

            try:

                css = css_file.read_text(
                    encoding="utf-8"
                )

                st.markdown(
                    f"<style>{css}</style>",
                    unsafe_allow_html=True,
                )

                print(
                    "[FRONTEND] CSS loaded:",
                    css_file,
                )

                return

            except Exception as error:

                print(
                    "[FRONTEND CSS ERROR]",
                    repr(error),
                )

    print(
        "[FRONTEND] No frontend CSS file found."
    )


load_css()


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "active_feature": "Chat",
    "messages": [],
    "selected_document": "",
    "document_context": False,
    "ocr_text": "",
    "web_url": "",
    "web_context": False,
    "voice_audio": None,
    "voice_transcript": "",
    "processed_voice_hash": "",
}

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# TOP HEADER
#
# Uses st.html when available so HTML is NEVER displayed
# as raw Markdown/code.
# =========================================================

HEADER_HTML = """
<div class="app-header">
    <div class="brand">
        <div class="brand-icon">🤖</div>
        <div>
            <div class="brand-title">Agentic RAG Assistant</div>
            <div class="brand-subtitle">
                Intelligent document search • Web research • General AI • Vision & OCR • Voice
            </div>
        </div>
    </div>
    <div class="online-badge">
        <span class="online-dot"></span>
        System Online
    </div>
</div>
"""

if hasattr(st, "html"):
    st.html(HEADER_HTML)
else:
    st.markdown(
        HEADER_HTML,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

active_feature = render_sidebar()


# =========================================================
# PAGE HELPERS
# =========================================================

def page_header(
    title: str,
    subtitle: str,
) -> None:

    st.markdown(
        f'<div class="page-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# CHAT
# =========================================================

if active_feature == "Chat":

    page_header(
        "💬 Conversation",
        "Ask about your documents, webpages, images, or anything else.",
    )

    with st.container(
        border=True,
    ):

        render_chat()


# =========================================================
# DOCUMENT RAG
# =========================================================

elif active_feature == "Document RAG":

    page_header(
        "📄 Document RAG",
        "Upload documents and ask questions grounded in your knowledge base.",
    )

    left_col, right_col = st.columns(
        [2.1, 1],
        gap="large",
    )

    with left_col:

        st.markdown(
            '<div class="section-title">＋ Add Knowledge</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Upload PDF, DOCX, or TXT documents.'
            '</div>',
            unsafe_allow_html=True,
        )

        render_document_upload()

    with right_col:

        st.markdown(
            '<div class="section-title">📚 Knowledge Library</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Your indexed documents.'
            '</div>',
            unsafe_allow_html=True,
        )

        render_document_library()

    st.divider()

    st.markdown(
        '<div class="section-title">💬 Ask your documents</div>',
        unsafe_allow_html=True,
    )

    with st.container(
        border=True,
    ):

        render_chat()


# =========================================================
# WEB SEARCH
# =========================================================

elif active_feature == "Web Search":

    page_header(
        "🌐 Web Search",
        "Ask for current information and use the web-search route.",
    )

    st.info(
        "💡 Try: \"What are the latest AI developments?\""
    )

    with st.container(
        border=True,
    ):

        render_chat()


# =========================================================
# GENERAL AI
# =========================================================

elif active_feature == "General AI":

    page_header(
        "🤖 General AI",
        "Ask normal questions and have a general conversation with the assistant.",
    )

    with st.container(
        border=True,
    ):

        render_chat()


# =========================================================
# VISION & OCR
# =========================================================

elif active_feature == "Vision & OCR":

    page_header(
        "🖼️ Vision & OCR",
        "Upload an image and extract or understand its content.",
    )

    render_image_upload()

    if st.session_state.get("ocr_text"):

        st.divider()

        st.markdown(
            '<div class="section-title">📝 Extracted Text</div>',
            unsafe_allow_html=True,
        )

        st.text_area(
            "OCR Result",
            value=st.session_state.ocr_text,
            height=220,
            disabled=True,
        )

    st.divider()

    st.markdown(
        '<div class="section-title">💬 Ask about the image</div>',
        unsafe_allow_html=True,
    )

    with st.container(
        border=True,
    ):

        render_chat()


# =========================================================
# VOICE ASSISTANT
# =========================================================

elif active_feature == "Voice Assistant":

    if hasattr(st, "html"):

        st.html(
            """
            <div class="voice-card">
                <div class="voice-title">🎙️ Voice Assistant</div>
                <div class="voice-subtitle">
                    Speak your question and let the Agentic RAG Assistant handle it.
                </div>
            </div>
            """
        )

    else:

        st.markdown(
            '<div class="voice-card">'
            '<div class="voice-title">🎙️ Voice Assistant</div>'
            '<div class="voice-subtitle">'
            'Speak your question and let the Agentic RAG Assistant handle it.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # EXISTING VOICE COMPONENT
    # -----------------------------------------------------

    if VOICE_COMPONENT_AVAILABLE:

        render_voice_input()

    else:

        st.markdown(
            "### 🎤 Record your question"
        )

        st.caption(
            "Use the microphone below to record your question."
        )

        audio = st.audio_input(
            "🎤 Record Audio",
            key="native_voice_recorder",
        )

        if audio is not None:

            st.session_state.voice_audio = audio

            st.success(
                "✅ Voice recording captured."
            )

            st.audio(
                audio,
                format="audio/wav",
            )

    # -----------------------------------------------------
    # VOICE CONVERSATION
    # -----------------------------------------------------

    if st.session_state.messages:

        st.divider()

        st.markdown(
            '<div class="section-title">💬 Voice Conversation</div>',
            unsafe_allow_html=True,
        )

        with st.container(
            border=True,
        ):

            for message in st.session_state.messages:

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

                with st.chat_message(role):

                    st.markdown(content)

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

                    audio_data = message.get(
                        "audio"
                    )

                    if audio_data:

                        try:

                            st.audio(
                                audio_data,
                                format="audio/wav",
                            )

                        except Exception as error:

                            print(
                                "[VOICE] AUDIO DISPLAY ERROR:",
                                repr(error),
                            )


# =========================================================
# IMPORTANT
#
# NO FOOTER.
# NO TECHNOLOGY STACK TEXT.
# NO ARCHITECTURE TEXT.
# =========================================================
