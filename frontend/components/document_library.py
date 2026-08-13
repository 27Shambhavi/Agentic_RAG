import streamlit as st

from frontend.utils.api_client import api_client


# =========================================================
# DOCUMENT LIBRARY
# =========================================================

def render_document_library():

    # =====================================================
    # UPLOAD
    # =====================================================

    st.markdown(
        "#### 📤 Add Document"
    )

    st.caption(
        "Upload a PDF to your knowledge base."
    )

    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"],
        key="knowledge_pdf_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:

        st.caption(
            f"📄 {uploaded_file.name}"
        )

        if st.button(
            "⬆️ Upload PDF",
            use_container_width=True,
            key="upload_pdf",
        ):

            try:

                with st.spinner(
                    "Uploading and indexing..."
                ):

                    result = api_client.upload_document(
                        uploaded_file
                    )

                st.success(
                    "PDF uploaded and indexed."
                )

                # Clear uploader state
                if "knowledge_pdf_uploader" in st.session_state:
                    del st.session_state[
                        "knowledge_pdf_uploader"
                    ]

                st.rerun()

            except Exception as error:

                st.error(
                    f"Upload failed: {error}"
                )


    st.divider()


    # =====================================================
    # KNOWLEDGE BASE
    # =====================================================

    st.markdown(
        "#### 📚 Knowledge Base"
    )

    st.caption(
        "Your indexed documents"
    )


    # =====================================================
    # REFRESH
    # =====================================================

    if st.button(
        "↻ Refresh",
        use_container_width=True,
        key="refresh_documents",
    ):

        st.rerun()


    # =====================================================
    # LOAD DOCUMENTS
    # =====================================================

    try:

        documents = api_client.get_documents()

    except Exception as error:

        st.error(
            f"Could not load documents: {error}"
        )

        return


    # =====================================================
    # EMPTY
    # =====================================================

    if not documents:

        st.info(
            "📭 No documents uploaded yet."
        )

        return


    # =====================================================
    # NORMALIZE
    # =====================================================

    normalized = []

    for document in documents:

        filename = document.get(
            "filename",
            "",
        )

        display_name = document.get(
            "display_name",
            "",
        )

        if not display_name:
            display_name = filename

        normalized.append(
            {
                "filename": filename,
                "display_name": display_name,
                "size_kb": document.get(
                    "size_kb",
                    0,
                ),
            }
        )


    # =====================================================
    # SELECT DOCUMENT
    # =====================================================

    names = [
        doc["display_name"]
        for doc in normalized
    ]

    current = st.session_state.get(
        "selected_document",
        "",
    )

    default_index = 0

    if current in names:

        default_index = names.index(
            current
        )

    selected_name = st.selectbox(
        "Select document",
        names,
        index=default_index,
        key="document_selector",
    )


    # =====================================================
    # FIND DOCUMENT
    # =====================================================

    selected = next(
        (
            doc
            for doc in normalized
            if doc["display_name"] == selected_name
        ),
        None,
    )

    if selected is None:
        return


    # =====================================================
    # DOCUMENT CHANGE
    # =====================================================

    if (
        st.session_state.get("selected_document")
        != selected["display_name"]
    ):

        st.session_state.selected_document = (
            selected["display_name"]
        )

        # Selecting a document makes it available
        # as document context, but classifier still
        # decides whether a question is RAG.
        st.session_state.document_context = True


    # =====================================================
    # ACTIVE DOCUMENT
    # =====================================================

    st.success(
        f"📄 Active: {selected['display_name']}"
    )

    st.caption(
        f"{selected['size_kb']} KB • PDF"
    )


    # =====================================================
    # OPEN PDF
    # =====================================================

    pdf_url = api_client.get_document_url(
        selected["filename"]
    )

    st.link_button(
        "👁️ Open PDF",
        pdf_url,
        use_container_width=True,
    )