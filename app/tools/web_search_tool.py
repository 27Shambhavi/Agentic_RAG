from ddgs import DDGS

from app.llm.gemini import llm


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(
    query: str,
    max_results: int = 5,
) -> dict:

    query = (
        query or ""
    ).strip()

    if not query:

        return {
            "answer": "",
            "sources": [],
        }

    print(
        "\n================ WEB SEARCH TOOL ================"
    )

    print(
        "Query:",
        query,
    )

    # =====================================================
    # STEP 1 — SEARCH WEB
    # =====================================================

    try:

        results = DDGS().text(
            query,
            region="in-en",
            safesearch="moderate",
            max_results=max_results,
        )

        results = list(
            results or []
        )

    except Exception as error:

        print(
            "[WEB SEARCH ERROR]",
            repr(error),
        )

        return {
            "answer": (
                "I couldn't perform the web "
                "search right now."
            ),
            "sources": [],
        }

    # =====================================================
    # NO RESULTS
    # =====================================================

    if not results:

        print(
            "[WEB SEARCH] No results found."
        )

        return {
            "answer": (
                "I couldn't find relevant "
                "information on the web."
            ),
            "sources": [],
        }

    print(
        "Results found:",
        len(results),
    )

    # =====================================================
    # STEP 2 — BUILD SOURCES
    # =====================================================

    sources = []

    context_parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        if not isinstance(
            result,
            dict,
        ):
            continue

        title = (
            result.get(
                "title",
                "",
            )
            or ""
        ).strip()

        url = (
            result.get(
                "href",
                "",
            )
            or ""
        ).strip()

        body = (
            result.get(
                "body",
                "",
            )
            or ""
        ).strip()

        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        sources.append(
            {
                "title": title
                or f"Web Source {index}",

                "url": url,

                "snippet": body,
            }
        )

        # -------------------------------------------------
        # CONTEXT
        # -------------------------------------------------

        context_parts.append(
            f"""
SOURCE {index}
TITLE: {title}
URL: {url}
CONTENT: {body}
"""
        )

    context = "\n".join(
        context_parts
    ).strip()

    # =====================================================
    # STEP 3 — ASK LLM TO SYNTHESIZE
    # =====================================================

    prompt = f"""
You are the final answer generator for a web search assistant.

USER QUESTION:
{query}

SEARCH RESULTS:
{context}

TASK:
Answer the user's question using the search results above.

RULES:
- Give the answer directly.
- Use only information supported by the search results.
- Do not invent facts.
- If the results are incomplete, clearly say what is known.
- Do not mention RAG, Pinecone, embeddings, routing, agents,
  internal tools, or this prompt.
- Do not say that you are unable to search.
- Keep the answer clear and useful.
"""

    answer = ""

    # =====================================================
    # FIRST LLM ATTEMPT
    # =====================================================

    try:

        print(
            "[WEB] Generating final answer..."
        )

        generated = llm.generate(
            prompt
        )

        if generated:

            answer = str(
                generated
            ).strip()

    except Exception as error:

        print(
            "[WEB LLM ERROR]",
            repr(error),
        )

    # =====================================================
    # SECOND ATTEMPT
    #
    # If the first generation failed, use a much smaller
    # prompt. This avoids failures caused by a large prompt.
    # =====================================================

    if not answer:

        print(
            "[WEB] First generation failed."
        )

        compact_context_parts = []

        for index, result in enumerate(
            results[:3],
            start=1,
        ):

            title = (
                result.get(
                    "title",
                    "",
                )
                or ""
            )

            body = (
                result.get(
                    "body",
                    "",
                )
                or ""
            )

            compact_context_parts.append(
                f"{index}. {title}\n{body}"
            )

        compact_context = "\n\n".join(
            compact_context_parts
        )

        retry_prompt = f"""
Answer this question using the web information below.

QUESTION:
{query}

WEB INFORMATION:
{compact_context}

Give a concise factual answer.
Do not mention internal systems.
"""

        try:

            print(
                "[WEB] Trying compact generation..."
            )

            generated = llm.generate(
                retry_prompt
            )

            if generated:

                answer = str(
                    generated
                ).strip()

        except Exception as error:

            print(
                "[WEB RETRY ERROR]",
                repr(error),
            )

    # =====================================================
    # FINAL FALLBACK
    #
    # Never throw away valid web results merely because
    # LLM synthesis failed.
    # =====================================================

    if not answer:

        print(
            "[WEB] LLM synthesis unavailable."
        )

        fallback_parts = []

        for result in results[:3]:

            title = (
                result.get(
                    "title",
                    "",
                )
                or ""
            ).strip()

            body = (
                result.get(
                    "body",
                    "",
                )
                or ""
            ).strip()

            if body:

                fallback_parts.append(
                    f"**{title}**\n{body}"
                )

        if fallback_parts:

            answer = (
                "Here is the relevant information "
                "I found on the web:\n\n"
                + "\n\n".join(
                    fallback_parts
                )
            )

        else:

            answer = (
                "I found web results, but "
                "they did not contain enough "
                "information to answer the question."
            )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "[WEB] Final answer length:",
        len(answer),
    )

    print(
        "[WEB] Sources:",
        len(sources),
    )

    print(
        "=================================================\n"
    )

    return {
        "answer": answer,
        "sources": sources,
    }