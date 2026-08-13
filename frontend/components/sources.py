import streamlit as st


def render_sources(
    sources: list
):

    if not sources:
        return

    with st.expander(
        f"📚 Sources ({len(sources)})"
    ):

        for index, source in enumerate(
            sources,
            start=1
        ):

            # -------------------------------------------------
            # WEB SOURCE
            # -------------------------------------------------

            if source.get("url"):

                title = source.get(
                    "title",
                    f"Source {index}"
                )

                url = source.get(
                    "url",
                    ""
                )

                snippet = source.get(
                    "snippet",
                    ""
                )

                st.markdown(
                    f"**{index}. [{title}]({url})**"
                )

                if snippet:

                    st.caption(
                        snippet
                    )

            # -------------------------------------------------
            # RAG SOURCE
            # -------------------------------------------------

            else:

                source_name = source.get(
                    "source",
                    "Unknown document"
                )

                page = source.get(
                    "page",
                    "?"
                )

                score = source.get(
                    "score"
                )

                if score is not None:

                    st.markdown(
                        f"**{index}. 📄 "
                        f"{source_name}**  \n"
                        f"Page: {page} • "
                        f"Score: {score:.4f}"
                    )

                else:

                    st.markdown(
                        f"**{index}. 📄 "
                        f"{source_name}**  \n"
                        f"Page: {page}"
                    )