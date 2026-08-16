from __future__ import annotations

import streamlit as st


# =========================================================
# FEATURES
# =========================================================

FEATURES = [
    ("Chat", "💬", "Ask anything and interact with the assistant."),
    ("Document RAG", "📄", "Search and ask questions from your documents."),
    ("Web Search", "🌐", "Search the web for current information."),
    ("General AI", "🤖", "Have a normal conversation with the AI."),
    ("Vision & OCR", "🖼️", "Upload an image and work with extracted text."),
    ("Voice Assistant", "🎙️", "Speak naturally using the voice interface."),
]


# =========================================================
# HTML HELPER
#
# st.html prevents HTML from being interpreted as a
# Markdown code block. Fallback is kept for older Streamlit.
# =========================================================

def _html(content: str) -> None:
    content = content.strip()

    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(
            content,
            unsafe_allow_html=True,
        )


# =========================================================
# NEW CONVERSATION
# =========================================================

def _new_conversation() -> None:
    st.session_state.messages = []

    st.session_state.voice_response_requested = False
    st.session_state.voice_audio = None

    # A new conversation should not keep an old webpage
    # context accidentally.
    st.session_state.web_url = ""
    st.session_state.web_context = False

    # Keep selected document/library selection intact.
    st.session_state.document_context = bool(
        st.session_state.get("selected_document", "")
    )


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar() -> str:

    if "active_feature" not in st.session_state:
        st.session_state.active_feature = "Chat"

    active_feature = st.session_state.active_feature

    with st.sidebar:

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        _html(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🤖</div>
                <div class="sidebar-brand-copy">
                    <div class="sidebar-brand-title">Agentic RAG</div>
                    <div class="sidebar-brand-subtitle">Intelligent AI Assistant</div>
                </div>
            </div>
            """
        )

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # FEATURES
        # -------------------------------------------------

        st.markdown(
            '<div class="sidebar-section-label">Features</div>',
            unsafe_allow_html=True,
        )

        for feature_name, icon, description in FEATURES:

            is_active = (
                active_feature == feature_name
            )

            button_label = (
                f"{icon}  {feature_name}"
            )

            if st.button(
                button_label,
                key=f"feature_{feature_name}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_feature = feature_name
                st.rerun()

        # -------------------------------------------------
        # CONVERSATION
        # -------------------------------------------------

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section-label">Conversation</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "＋  New Conversation",
            key="new_conversation",
            use_container_width=True,
        ):
            _new_conversation()
            st.rerun()

        st.caption(
            "Start a fresh conversation without removing "
            "your document library."
        )

        # -------------------------------------------------
        # ACTIVE FEATURE
        # -------------------------------------------------

        current = next(
            (
                item
                for item in FEATURES
                if item[0] == active_feature
            ),
            FEATURES[0],
        )

        feature_name, icon, description = current

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section-label">Active Feature</div>',
            unsafe_allow_html=True,
        )

        _html(
            f"""
            <div class="active-feature-card">
                <div class="active-feature-title">
                    {icon} {feature_name}
                </div>
                <div class="active-feature-description">
                    {description}
                </div>
            </div>
            """
        )

        # -------------------------------------------------
        # SYSTEM STATUS
        # -------------------------------------------------

        _html(
            """
            <div class="system-status-card">
                <div class="system-status-title">
                    <span class="system-status-dot"></span>
                    System Online
                </div>
                <div class="system-status-text">
                    All frontend services are ready.
                </div>
            </div>
            """
        )

    return active_feature
