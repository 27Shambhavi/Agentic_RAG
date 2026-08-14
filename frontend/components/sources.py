import streamlit as st


# =========================================================
# SOURCES RENDERER
# =========================================================

def render_sources(
    sources: list,
):
    """
    Render web and document sources.

    Supported source formats:

    WEB:
    {
        "title": "...",
        "url": "...",
        "snippet": "..."
    }

    RAG:
    {
        "source": "...",
        "page": 1,
        "score": 0.82,
        "text": "..."
    }
    """

    if not sources:
        return

    # -----------------------------------------------------
    # SOURCE CONTAINER
    # -----------------------------------------------------

    with st.expander(
        f"📚 Sources ({len(sources)})",
        expanded=False,
    ):

        for index, source in enumerate(
            sources,
            start=1,
        ):

            if not isinstance(
                source,
                dict,
            ):
                continue

            # =================================================
            # WEB SOURCE
            # =================================================

            url = (
                source.get(
                    "url",
                    "",
                )
                or ""
            ).strip()

            if url:

                title = (
                    source.get(
                        "title",
                        "",
                    )
                    or ""
                ).strip()

                if not title:
                    title = f"Web Source {index}"

                snippet = (
                    source.get(
                        "snippet",
                        "",
                    )
                    or ""
                ).strip()

                # -------------------------------------------------
                # TITLE + LINK
                # -------------------------------------------------

                st.markdown(
                    f"**{index}. [{title}]({url})**"
                )

                # -------------------------------------------------
                # URL
                # -------------------------------------------------

                st.caption(
                    url
                )

                # -------------------------------------------------
                # SNIPPET
                # -------------------------------------------------

                if snippet:

                    st.write(
                        snippet
                    )

                st.divider()

                continue

            # =================================================
            # DOCUMENT / RAG SOURCE
            # =================================================

            source_name = (
                source.get(
                    "source",
                    "",
                )
                or "Unknown document"
            )

            page = source.get(
                "page",
                "?",
            )

            score = source.get(
                "score",
                None,
            )

            # -------------------------------------------------
            # DOCUMENT HEADER
            # -------------------------------------------------

            st.markdown(
                f"**{index}. 📄 {source_name}**"
            )

            # -------------------------------------------------
            # METADATA
            # -------------------------------------------------

            metadata = (
                f"Page: {page}"
            )

            if score is not None:

                try:

                    metadata += (
                        f" • Relevance: "
                        f"{float(score):.4f}"
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

            st.caption(
                metadata
            )

            # -------------------------------------------------
            # CHUNK TEXT
            # -------------------------------------------------

            text = (
                source.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            if text:

                with st.container():

                    st.write(
                        text
                    )

            st.divider()