import streamlit as st

from frontend.utils.api_client import api_client


# =========================================================
# DOCUMENT LIBRARY
# =========================================================

def render_document_library():

    st.markdown("#### 📤 Add Document")
    st.caption("Upload a PDF to your knowledge base.")

    # =====================================================
    # UPLOAD
    # =====================================================

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

                display_name = (
                    result.get(
                        "display_name",
                        uploaded_file.name,
                    )
                    or uploaded_file.name
                )

                # -----------------------------------------
                # ONLY STORE THE ACTUALLY UPLOADED DOCUMENT
                # -----------------------------------------

                st.session_state.selected_document = (
                    display_name
                )

                st.session_state.document_context = True

                st.success(
                    f"Uploaded: {display_name}"
                )

                # Clear uploader
                st.session_state.pop(
                    "knowledge_pdf_uploader",
                    None,
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Upload failed: {error}"
                )

    st.divider()

    # =====================================================
    # KNOWLEDGE BASE
    # =====================================================

    st.markdown("#### 📚 Knowledge Base")
    st.caption("Your uploaded documents")

    # =====================================================
    # REFRESH
    # =====================================================

    if st.button(
        "🔄 Refresh",
        use_container_width=True,
        key="refresh_documents",
    ):

        st.rerun()

    # =====================================================
    # GET DOCUMENTS FROM BACKEND
    # =====================================================

    try:

        documents = api_client.get_documents()

    except Exception as error:

        st.error(
            f"Could not load documents: {error}"
        )

        return

    # =====================================================
    # NORMALIZE BACKEND RESPONSE
    # =====================================================

    if not isinstance(
        documents,
        list,
    ):

        documents = []

    normalized = []

    for document in documents:

        if not isinstance(
            document,
            dict,
        ):
            continue

        filename = (
            document.get(
                "filename",
                "",
            )
            or ""
        ).strip()

        display_name = (
            document.get(
                "display_name",
                "",
            )
            or filename
        ).strip()

        # Ignore invalid records
        if not filename or not display_name:
            continue

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
    # NOTHING UPLOADED
    # =====================================================

    if not normalized:

        # Remove stale document selection
        st.session_state.pop(
            "selected_document",
            None,
        )

        st.session_state.document_context = False

        st.info(
            "📭 No documents uploaded yet."
        )

        return

    # =====================================================
    # DOCUMENT NAMES
    # =====================================================

    names = [
        document["display_name"]
        for document in normalized
    ]

    # =====================================================
    # CURRENT DOCUMENT
    # =====================================================

    current = (
        st.session_state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    # If current document no longer exists,
    # automatically select the first backend document.

    if current not in names:

        current = names[0]

        st.session_state.selected_document = (
            current
        )

    # =====================================================
    # SELECT DOCUMENT
    # =====================================================

    selected_name = st.selectbox(
        "Select document",
        names,
        index=names.index(current),
        key="document_selector",
    )

    # =====================================================
    # SYNC SELECTION
    # =====================================================

    if selected_name != st.session_state.get(
        "selected_document",
        "",
    ):

        st.session_state.selected_document = (
            selected_name
        )

        st.session_state.document_context = True

    # =====================================================
    # FIND SELECTED DOCUMENT
    # =====================================================

    selected = next(
        (
            document
            for document in normalized
            if document["display_name"] == selected_name
        ),
        None,
    )

    if selected is None:
        return

    # =====================================================
    # ACTIVE DOCUMENT
    # =====================================================

    st.success(
        f"📄 Uploaded PDF: {selected['display_name']}"
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