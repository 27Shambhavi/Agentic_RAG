import streamlit as st


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        # =================================================
        # BRAND
        # =================================================

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">🤖</div>
                <div>
                    <div class="sidebar-title">
                        Agentic RAG
                    </div>
                    <div class="sidebar-subtitle">
                        Multimodal AI Assistant
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()


        # =================================================
        # WORKSPACE
        # =================================================

        st.markdown(
            "### Workspace"
        )


        # -------------------------------------------------
        # NEW CONVERSATION
        # -------------------------------------------------

        if st.button(
            "＋ New Conversation",
            use_container_width=True,
            key="sidebar_new",
        ):

            st.session_state.messages = []

            st.session_state.document_context = False

            st.session_state.active_tool = (
                "conversation"
            )

            st.rerun()


        # -------------------------------------------------
        # CONVERSATION
        # -------------------------------------------------

        if st.button(
            "💬 Conversation",
            use_container_width=True,
            key="sidebar_conversation",
        ):

            st.session_state.active_tool = (
                "conversation"
            )

            st.rerun()


        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        if st.button(
            "🖼️ Vision & OCR",
            use_container_width=True,
            key="sidebar_ocr",
        ):

            st.session_state.active_tool = "ocr"

            st.rerun()


        st.divider()


        # =================================================
        # ACTIVE
        # =================================================

        active_tool = st.session_state.get(
            "active_tool",
            "conversation",
        )


        labels = {
            "conversation": "💬 Conversation",
            "ocr": "🖼️ Vision & OCR",
        }


        active_label = labels.get(
            active_tool,
            "💬 Conversation",
        )


        st.markdown(
            "### Active"
        )

        st.markdown(
            f"""
            <div class="active-tool">
                <div class="active-dot"></div>
                <div>
                    <div class="active-name">
                        {active_label}
                    </div>
                    <div class="active-label">
                        Current workspace
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )

        st.caption(
            "Agentic RAG Assistant v1.0"
        )