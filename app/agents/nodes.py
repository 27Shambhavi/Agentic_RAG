from __future__ import annotations

from app.agents.state import AgentState

from app.rag.document_rag import document_rag
from app.rag.retriever import retrieve

from app.llm.gemini import llm


RAG_RELEVANCE_THRESHOLD = 0.15


# =========================================================
# HELPERS
# =========================================================

def safe_history(
    state: AgentState,
) -> list[dict]:

    history = state.get(
        "history",
        [],
    )

    return (
        history
        if isinstance(
            history,
            list,
        )
        else []
    )


def build_history_text(
    history: list[dict],
) -> str:

    parts = []

    for message in history[-6:]:

        if not isinstance(
            message,
            dict,
        ):
            continue

        role = str(
            message.get(
                "role",
                "user",
            )
        ).upper()

        content = str(
            message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if content:

            parts.append(
                f"{role}: {content}"
            )

    return (
        "\n".join(parts)
        if parts
        else "No previous conversation."
    )


# =========================================================
# RAG RETRIEVAL
# =========================================================

def get_document_matches(
    query: str,
) -> list[dict]:

    try:

        return retrieve(
            query=query,
            top_k=8,
        )

    except Exception as error:

        print(
            "[RAG RETRIEVAL ERROR]",
            repr(error),
        )

        return []


def get_best_document_score(
    matches: list[dict],
) -> float:

    scores = []

    for match in matches:

        try:

            scores.append(
                float(
                    match.get(
                        "score",
                        0.0,
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    return (
        max(scores)
        if scores
        else 0.0
    )


# =========================================================
# RAG NODE
# =========================================================

def rag_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    selected_document = (
        state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    if not query:

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": [],

            "rag_found": False,
        }

    print(
        "\n================ RAG NODE ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    print(
        "Retrieval scope: ENTIRE KNOWLEDGE BASE"
    )

    # =====================================================
    # RETRIEVE
    # =====================================================

    matches = get_document_matches(
        query
    )

    best_score = (
        get_best_document_score(
            matches
        )
    )

    print(
        "Retrieved chunks:",
        len(matches),
    )

    print(
        "Best score:",
        best_score,
    )

    # =====================================================
    # NO MATCH
    # =====================================================

    if not matches:

        print(
            "[RAG] No knowledge-base match."
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": [],

            "relevance_score": 0.0,

            "rag_found": False,

            "fallback_reason": (
                "No relevant knowledge-base match."
            ),
        }

    # =====================================================
    # THRESHOLD
    # =====================================================

    if (
        best_score
        < RAG_RELEVANCE_THRESHOLD
    ):

        print(
            "[RAG] Below relevance threshold."
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": matches,

            "relevance_score": best_score,

            "rag_found": False,

            "fallback_reason": (
                "Knowledge-base relevance below threshold."
            ),
        }

    # =====================================================
    # GENERATE
    # =====================================================

    try:

        result = document_rag(

            query=query,

            selected_document=(
                selected_document
            ),

            history=history,

            documents=matches,
        )

    except Exception as error:

        print(
            "[RAG GENERATION ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": matches,

            "relevance_score": best_score,

            "rag_found": False,

            "fallback_reason": (
                "Document answer generation failed."
            ),
        }

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": matches,

            "relevance_score": best_score,

            "rag_found": False,
        }

    answer = (
        result.get(
            "answer",
            "",
        )
        or ""
    ).strip()

    sources = (
        result.get(
            "sources",
            [],
        )
        or matches
    )

    relevant = result.get(
        "relevant",
        False,
    )

    # =====================================================
    # NOT RELEVANT
    # =====================================================

    if (
        relevant is False
        or not answer
    ):

        print(
            "[RAG] Answer not found."
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": sources,

            "selected_document": (
                selected_document
            ),

            "document_context": bool(
                selected_document
            ),

            "relevance_score": best_score,

            "rag_found": False,
        }

    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        "[RAG] SUCCESS"
    )

    return {
        **state,

        "route": "rag",

        "answer": answer,

        "sources": sources,

        "selected_document": (
            selected_document
        ),

        "document_context": bool(
            selected_document
        ),

        "relevance_score": best_score,

        "rag_found": True,
    }


# =========================================================
# GENERAL
# =========================================================

def general_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    prompt = f"""
You are a helpful general AI assistant.

CONVERSATION:
{build_history_text(history)}

USER:
{query}

Answer naturally and directly.
"""

    try:

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

        if answer:

            return {
                **state,

                "route": "general",

                "answer": answer,

                "sources": [],
            }

    except Exception as error:

        print(
            "[GENERAL ERROR]",
            repr(error),
        )

    # If general LLM fails, use web.
    return web_node(
        {
            **state,

            "route": "web",
        }
    )


# =========================================================
# GREETING
# =========================================================

def greeting_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    prompt = f"""
You are a friendly AI assistant.

CONVERSATION:
{build_history_text(history)}

USER:
{query}

Respond naturally to the user.

Do not give a generic fixed greeting.
Adapt your response to what the user said.
"""

    try:

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

    except Exception as error:

        print(
            "[GREETING ERROR]",
            repr(error),
        )

        answer = (
            "Hello! How can I help you?"
        )

    return {
        **state,

        "route": "greeting",

        "answer": answer,

        "sources": [],
    }


# =========================================================
# WEB SEARCH
# =========================================================

def web_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    if not query:

        return {
            **state,

            "route": "web",

            "answer": "",

            "sources": [],
        }

    print(
        "\n================ WEB NODE ================"
    )

    print(
        "Query:",
        query,
    )

    try:

        from app.tools.web_search_tool import (
            web_search,
        )

        result = web_search(
            query=query,
            max_results=5,
        )

        if not isinstance(
            result,
            dict,
        ):

            return {
                **state,

                "route": "web",

                "answer": str(result),

                "sources": [],
            }

        answer = (
            result.get(
                "answer",
                "",
            )
            or ""
        ).strip()

        sources = (
            result.get(
                "sources",
                [],
            )
            or []
        )

        if answer:

            return {
                **state,

                "route": "web",

                "answer": answer,

                "sources": sources,

                "web_context": False,
            }

        # -------------------------------------------------
        # SOURCE SYNTHESIS
        # -------------------------------------------------

        source_parts = []

        for index, source in enumerate(
            sources[:5],
            start=1,
        ):

            if not isinstance(
                source,
                dict,
            ):
                continue

            source_parts.append(
                f"""
SOURCE {index}

TITLE:
{source.get("title", "")}

CONTENT:
{source.get(
    "snippet",
    source.get(
        "content",
        source.get(
            "text",
            "",
        ),
    ),
)}

URL:
{source.get(
    "url",
    source.get(
        "link",
        "",
    ),
)}
"""
            )

        if source_parts:

            prompt = f"""
Answer the user's question using ONLY
the following web search results.

USER:
{query}

RESULTS:
{"".join(source_parts)}

Do not invent unsupported facts.
"""

            generated = llm.generate(
                prompt
            )

            generated = (
                generated or ""
            ).strip()

            if generated:

                return {
                    **state,

                    "route": "web",

                    "answer": generated,

                    "sources": sources,

                    "web_context": False,
                }

        return {
            **state,

            "route": "web",

            "answer": (
                "I found web results, but "
                "couldn't generate a reliable answer."
            ),

            "sources": sources,

            "web_context": False,
        }

    except Exception as error:

        print(
            "[WEB NODE ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "web",

            "answer": (
                "I couldn't perform the web search "
                "right now."
            ),

            "sources": [],
        }


# =========================================================
# WEB RAG
# =========================================================

def web_rag_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    web_url = (
        state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    if not web_url:

        return {
            **state,

            "route": "web",

            "answer": (
                "No active webpage is available."
            ),

            "sources": [],

            "web_context": False,
        }

    try:

        from app.rag.web_rag import (
            web_rag,
        )

        result = web_rag(

            query=query,

            url=web_url,

            history=history,
        )

    except Exception as error:

        print(
            "[WEB RAG ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "I couldn't retrieve and analyze "
                "the webpage right now."
            ),

            "sources": [],

            "web_url": web_url,

            "web_context": True,
        }

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "I couldn't generate a reliable "
                "answer from the webpage."
            ),

            "sources": [],

            "web_url": web_url,

            "web_context": True,
        }

    answer = (
        result.get(
            "answer",
            "",
        )
        or ""
    ).strip()

    sources = (
        result.get(
            "sources",
            [],
        )
        or []
    )

    relevant = result.get(
        "relevant",
        False,
    )

    title = (
        result.get(
            "title",
            "",
        )
        or ""
    )

    best_score = result.get(
        "best_score",
        None,
    )

    index_result = result.get(
        "index",
        {},
    )

    if not isinstance(
        index_result,
        dict,
    ):
        index_result = {}

    return {
        **state,

        "route": "web_rag",

        "answer": (
            answer
            if relevant and answer
            else (
                "I couldn't find enough relevant "
                "information on the provided webpage."
            )
        ),

        "sources": sources,

        "web_url": web_url,

        "web_context": True,

        "web_title": title,

        "web_scraper": (
            result.get(
                "scraping_method",
                "",
            )
            or ""
        ),

        "web_chunks": index_result.get(
            "chunks",
            0,
        ),

        "web_indexed": (
            index_result.get(
                "status",
                "",
            )
            == "indexed"
        ),

        "web_relevance_score": best_score,
    }


# =========================================================
# WEATHER
# =========================================================

def weather_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    try:

        from app.tools.weather_tool import (
            get_weather,
        )

        location_prompt = f"""
Extract the city/location from this weather request.

Return ONLY the location name.

QUESTION:
{query}
"""

        city = llm.generate(
            location_prompt
        )

        city = (
            city or ""
        ).strip().strip(
            "\"'"
        )

        if not city:

            return {
                **state,

                "route": "weather",

                "answer": (
                    "Please specify a city or location."
                ),

                "sources": [],
            }

        result = get_weather(
            city
        )

        if not isinstance(
            result,
            dict,
        ):

            return {
                **state,

                "route": "weather",

                "answer": str(result),

                "sources": [],
            }

        return {
            **state,

            "route": "weather",

            "answer": (
                result.get(
                    "answer",
                    "",
                )
                or ""
            ),

            "sources": (
                result.get(
                    "sources",
                    [],
                )
                or []
            ),
        }

    except Exception as error:

        print(
            "[WEATHER ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "weather",

            "answer": (
                "I couldn't retrieve the weather."
            ),

            "sources": [],
        }


# =========================================================
# OCR
# =========================================================

def ocr_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    ocr_text = (
        state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    if not ocr_text:

        return {
            **state,

            "route": "ocr",

            "answer": (
                "No image text is available."
            ),

            "sources": [],
        }

    prompt = f"""
Answer the user's question using ONLY
the OCR text below.

OCR:
{ocr_text}

HISTORY:
{build_history_text(history)}

QUESTION:
{query}

If the answer is not present in the OCR text,
say that it cannot be found in the image.
"""

    try:

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

    except Exception as error:

        print(
            "[OCR ERROR]",
            repr(error),
        )

        answer = (
            "I couldn't answer from the image."
        )

    return {
        **state,

        "route": "ocr",

        "answer": answer,

        "sources": [],
    }