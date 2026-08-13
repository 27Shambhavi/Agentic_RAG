import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
# IMPORT COMPONENTS
# =========================================================

from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat
from frontend.components.document_library import (
    render_document_library,
)
from frontend.components.voice_input import (
    render_voice_input,
)
from frontend.components.image_upload import (
    render_image_upload,
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css():

    css_paths = [
        PROJECT_ROOT / "frontend" / "styles" / "main.css",
        PROJECT_ROOT / "frontend" / "style.css",
    ]

    for css_path in css_paths:

        if css_path.exists():

            css = css_path.read_text(
                encoding="utf-8"
            )

            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True,
            )

            break


load_css()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "active_tool": "conversation",
    "messages": [],
    "selected_document": "",
    "document_context": False,
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# NEW CONVERSATION
# =========================================================

def new_conversation():

    # Only clear conversation state.
    # Do NOT delete uploaded documents.
    st.session_state.messages = []

    # Disable current document context for this conversation.
    st.session_state.document_context = False

    # Always return to normal chat.
    st.session_state.active_tool = "conversation"


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns(
    [5, 1],
    vertical_alignment="center",
)


with header_left:

    st.markdown(
        "## 🤖 Agentic RAG Assistant"
    )

    st.caption(
        "Documents • Web • AI • OCR • Voice"
    )


with header_right:

    if st.button(
        "＋ New",
        use_container_width=True,
        key="top_new_conversation",
    ):

        new_conversation()

        st.rerun()


st.divider()


# =========================================================
# MAIN LAYOUT
# =========================================================

conversation_col, knowledge_col = st.columns(
    [3.5, 1.25],
    gap="large",
)


# =========================================================
# MAIN CONVERSATION
# =========================================================

with conversation_col:

    active_tool = st.session_state.get(
        "active_tool",
        "conversation",
    )


    # =====================================================
    # CONVERSATION
    # =====================================================

    if active_tool == "conversation":

        # IMPORTANT:
        # Do not create another "Conversation" heading here.
        # chat.py owns the conversation UI.

        render_chat()

        # -------------------------------------------------
        # COMPACT VOICE INPUT
        # -------------------------------------------------

        with st.expander(
            "🎙️ Voice input",
            expanded=False,
        ):

            render_voice_input()


    # =====================================================
    # OCR
    # =====================================================

    elif active_tool == "ocr":

        st.markdown(
            "### 🖼️ Vision & OCR"
        )

        st.caption(
            "Extract text and ask questions about images."
        )

        render_image_upload()


    # =====================================================
    # VOICE
    # =====================================================

    elif active_tool == "voice":

        # Backward compatibility only.
        # Voice should normally be used inside conversation.

        st.session_state.active_tool = "conversation"

        st.rerun()


    # =====================================================
    # FALLBACK
    # =====================================================

    else:

        st.session_state.active_tool = "conversation"

        st.rerun()


# =========================================================
# RIGHT — KNOWLEDGE
# =========================================================

with knowledge_col:

    st.markdown(
        "### 📚 Knowledge"
    )

    st.caption(
        "Documents and knowledge base"
    )

    render_document_library()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Agentic RAG • FastAPI • LangGraph • "
    "Pinecone • Gemini • Mistral OCR"
)