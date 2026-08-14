import streamlit as st

from frontend.utils.api_client import api_client


def render_image_upload():

    st.markdown(
        """
        <div style="
            font-size: 15px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 3px;
        ">
            🖼️ Vision & OCR
        </div>

        <div style="
            font-size: 10px;
            color: #64748b;
            margin-bottom: 10px;
        ">
            Extract text and ask questions about images.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # UPLOAD
    # =====================================================

    uploaded_image = st.file_uploader(
        "Upload image",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="ocr_image",
        label_visibility="collapsed",
    )

    if uploaded_image is None:

        st.markdown(
            """
            <div style="
                padding: 18px 12px;
                text-align: center;
                border-radius: 13px;
                border: 1px dashed
                    rgba(148,163,184,0.20);
                color: #64748b;
                font-size: 10px;
            ">
                🖼️<br>
                Upload an image to begin
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    # =====================================================
    # PREVIEW
    # =====================================================

    st.image(
        uploaded_image,
        caption=uploaded_image.name,
        use_container_width=True,
    )

    # =====================================================
    # OCR
    # =====================================================

    if st.button(
        "🔍 Extract Text",
        use_container_width=True,
        type="primary",
        key="run_ocr",
    ):

        with st.spinner(
            "Reading image..."
        ):

            try:

                result = api_client.ocr_image(
                    uploaded_image
                )

                st.session_state[
                    "ocr_result"
                ] = result

                st.session_state[
                    "ocr_text"
                ] = result.get("text", "")

                st.success(
                    "✓ Text extracted"
                )

            except Exception as error:

                st.error(
                    f"OCR failed: {error}"
                )

    # =====================================================
    # OCR RESULT
    # =====================================================

    ocr_result = st.session_state.get(
        "ocr_result"
    )

    if not ocr_result:
        return

    extracted_text = ocr_result.get(
        "text",
        ""
    )

    if not extracted_text:

        st.warning(
            "No readable text detected."
        )

        return

    # =====================================================
    # OCR VIEW
    # =====================================================

    with st.expander(
        "📝 View extracted text"
    ):

        st.markdown(
            extracted_text
        )

    # =====================================================
    # ASK ABOUT IMAGE
    # =====================================================

    st.markdown(
        """
        <div style="
            font-size: 12px;
            font-weight: 650;
            color: #cbd5e1;
            margin-top: 8px;
            margin-bottom: 5px;
        ">
            💬 Ask about this image
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_input(
        "Question",
        placeholder="What is this image about?",
        key="image_question",
        label_visibility="collapsed",
    )

    if st.button(
        "🤖 Ask Agent",
        use_container_width=True,
        key="ask_image",
    ):

        if not question.strip():

            st.warning(
                "Enter a question first."
            )

            return

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        st.session_state.active_tool = "conversation"

        st.rerun()