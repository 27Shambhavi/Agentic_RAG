from ddgs import DDGS


# =========================================================
# DUCKDUCKGO / DDGS WEB SEARCH
# =========================================================

def web_search(
    query: str,
    max_results: int = 5,
) -> dict:

    query = (query or "").strip()

    if not query:
        return {
            "answer": "",
            "sources": [],
        }

    try:

        # -------------------------------------------------
        # SEARCH WEB
        # -------------------------------------------------

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=max_results,
                )
            )


        # -------------------------------------------------
        # NO RESULTS
        # -------------------------------------------------

        if not results:

            return {
                "answer": (
                    "I couldn't find relevant "
                    "web results for this question."
                ),
                "sources": [],
            }


        # -------------------------------------------------
        # BUILD SOURCES
        # -------------------------------------------------

        sources = []

        context_parts = []


        for index, result in enumerate(
            results,
            start=1,
        ):

            title = result.get(
                "title",
                "Untitled",
            )

            url = result.get(
                "href",
                "",
            )

            body = result.get(
                "body",
                "",
            )


            sources.append(
                {
                    "title": title,
                    "url": url,
                }
            )


            context_parts.append(
                f"""
SOURCE {index}

Title: {title}

URL: {url}

Content:
{body}
"""
            )


        # -------------------------------------------------
        # RETURN SEARCH CONTEXT
        #
        # nodes.py will use this result.
        # -------------------------------------------------

        return {
            "answer": "\n\n".join(
                context_parts
            ),
            "sources": sources,
        }


    except Exception as error:

        print(
            "[DDGS SEARCH ERROR]",
            repr(error),
        )

        return {
            "answer": (
                "Web search is currently "
                "unavailable."
            ),
            "sources": [],
        }