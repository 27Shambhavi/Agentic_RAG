import streamlit as st

from frontend.utils.api_client import api_client


def render_document_upload():

    st.markdown(
        "### 📤 Add Document"
    )

    st.caption(
        "Upload a PDF to add it to your AI knowledge base."
    )

    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Only PDF documents are supported."
    )

    if uploaded_file is None:

        st.caption(
            "PDF • Automatically chunked, embedded "
            "and stored in Pinecone"
        )

        return

    st.success(
        f"📄 {uploaded_file.name}"
    )

    if st.button(
        "⚡ Index Document",
        type="primary",
        use_container_width=True
    ):

        progress = st.progress(
            0,
            text="Starting document processing..."
        )

        try:

            progress.progress(
                25,
                text="Uploading PDF..."
            )

            progress.progress(
                50,
                text="Extracting and chunking..."
            )

            result = api_client.upload_document(
                uploaded_file
            )

            progress.progress(
                100,
                text="Document indexed!"
            )

            st.success(
                "✓ Added to knowledge base"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Pages",
                    result.get(
                        "pages",
                        0
                    )
                )

            with col2:

                st.metric(
                    "Chunks",
                    result.get(
                        "chunks",
                        0
                    )
                )

            st.session_state[
                "documents_updated"
            ] = True

        except Exception as error:

            st.error(
                f"Upload failed: {error}"
            )