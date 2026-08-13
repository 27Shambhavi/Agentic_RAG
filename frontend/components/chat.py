import streamlit as st

from frontend.utils.api_client import api_client
from frontend.components.sources import render_sources


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
    # CHAT HISTORY
    # =====================================================

    if "messages" not in st.session_state:

        st.session_state.messages = []


    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not st.session_state.messages:

        st.info(
            "👋 Start a conversation by asking a question below."
        )


    # =====================================================
    # DISPLAY HISTORY
    # =====================================================

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

            st.markdown(content)


            # ---------------------------------------------
            # ROUTE
            # ---------------------------------------------

            route = message.get(
                "route"
            )

            if route:

                route_labels = {
                    "rag": "📄 Document RAG",
                    "web": "🌐 Web Search",
                    "general": "🧠 General AI",
                    "greeting": "👋 Greeting",
                }

                label = route_labels.get(
                    route.lower(),
                    route.title(),
                )

                st.caption(
                    f"Route: {label}"
                )


            # ---------------------------------------------
            # SOURCES
            # ---------------------------------------------

            sources = message.get(
                "sources",
                [],
            )

            if sources:

                render_sources(
                    sources
                )


    # =====================================================
    # INPUT
    # =====================================================

    prompt = st.chat_input(
        "Ask something..."
    )

    if not prompt:
        return

    prompt = prompt.strip()

    if not prompt:
        return


    # =====================================================
    # USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )


    with st.chat_message("user"):

        st.markdown(prompt)


    # =====================================================
    # ASSISTANT
    # =====================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                # -----------------------------------------
                # CURRENT DOCUMENT CONTEXT
                # -----------------------------------------

                selected_document = (
                    st.session_state.get(
                        "selected_document",
                        "",
                    )
                )

                document_context = (
                    st.session_state.get(
                        "document_context",
                        False,
                    )
                )


                # -----------------------------------------
                # API
                # -----------------------------------------

                result = api_client.chat(
                    message=prompt,
                    selected_document=selected_document,
                    document_context=document_context,
                )


                # -----------------------------------------
                # RESPONSE
                # -----------------------------------------

                answer = result.get(
                    "answer",
                    "",
                )

                route = result.get(
                    "route",
                    "general",
                )

                sources = result.get(
                    "sources",
                    [],
                )


                if not answer:

                    answer = (
                        "Sorry, I couldn't generate "
                        "an answer."
                    )


                # -----------------------------------------
                # DISPLAY
                # -----------------------------------------

                st.markdown(
                    answer
                )


                route_labels = {
                    "rag": "📄 Document RAG",
                    "web": "🌐 Web Search",
                    "general": "🧠 General AI",
                    "greeting": "👋 Greeting",
                }

                label = route_labels.get(
                    route.lower(),
                    route.title(),
                )

                st.caption(
                    f"Route: {label}"
                )


                if sources:

                    render_sources(
                        sources
                    )


                # -----------------------------------------
                # SAVE
                # -----------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "route": route,
                        "sources": sources,
                    }
                )


            except Exception as error:

                st.error(
                    f"Backend error: {error}"
                )