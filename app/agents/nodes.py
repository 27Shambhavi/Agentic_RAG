from __future__ import annotations

import re
from typing import Any

from app.agents.state import AgentState

from app.rag.document_rag import document_rag
from app.rag.retriever import retrieve

from app.llm.gemini import llm


RAG_RELEVANCE_THRESHOLD = 0.15


# ============================================================
# SAFE VALUE HELPERS
# ============================================================

def safe_text(
    value: Any,
) -> str:
    """
    Safely convert a value to a stripped string.

    Prevents errors such as:

        AttributeError:
        'tuple' object has no attribute 'strip'
    """

    if value is None:
        return ""

    if isinstance(
        value,
        tuple,
    ):

        if len(value) == 1:
            value = value[0]

        else:
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

    return str(value).strip()


# ============================================================
# HISTORY
# ============================================================

def safe_history(
    state: AgentState,
) -> list[dict]:

    history = state.get(
        "history",
        [],
    )

    if not isinstance(
        history,
        list,
    ):
        return []

    return history


def build_history_text(
    history: list[dict],
) -> str:

    parts: list[str] = []

    for message in history[-8:]:

        if not isinstance(
            message,
            dict,
        ):
            continue

        role = safe_text(
            message.get(
                "role",
                "user",
            )
        ).upper()

        content = safe_text(
            message.get(
                "content",
                "",
            )
        )

        if content:

            parts.append(
                f"{role}: {content}"
            )

    if parts:
        return "\n".join(parts)

    return "No previous conversation."


# ============================================================
# URL HELPERS
# ============================================================

def extract_url(
    text: Any,
) -> str:

    text = safe_text(
        text
    )

    if not text:
        return ""

    match = re.search(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    return (
        match.group(0)
        .strip()
        .rstrip(
            ".,!?;:)]}"
        )
    )


def resolve_active_web_url(
    state: AgentState,
) -> str:

    # ========================================================
    # 1. CURRENT STATE
    # ========================================================

    for key in (
        "active_web_url",
        "web_url",
    ):

        value = safe_text(
            state.get(
                key,
                "",
            )
        )

        if value:
            return value

    # ========================================================
    # 2. STORED URL LIST
    # ========================================================

    urls = state.get(
        "web_urls",
        [],
    )

    if isinstance(
        urls,
        list,
    ):

        for url in reversed(
            urls
        ):

            value = safe_text(
                url
            )

            if value:
                return value

    # ========================================================
    # 3. CONVERSATION HISTORY
    # ========================================================

    history = safe_history(
        state
    )

    for message in reversed(
        history
    ):

        if not isinstance(
            message,
            dict,
        ):
            continue

        content = safe_text(
            message.get(
                "content",
                "",
            )
        )

        url = extract_url(
            content
        )

        if url:
            return url

    return ""


def update_web_url_state(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    current_url = extract_url(
        query
    )

    active_url = (
        current_url
        or resolve_active_web_url(
            state
        )
    )

    urls = state.get(
        "web_urls",
        [],
    )

    if not isinstance(
        urls,
        list,
    ):
        urls = []

    urls = list(
        urls
    )

    if current_url:

        if current_url not in urls:

            urls.append(
                current_url
            )

    return {
        **state,

        "active_web_url": active_url,

        "web_url": active_url,

        "web_urls": urls,
    }


# ============================================================
# DOCUMENT RETRIEVAL
# ============================================================

def get_document_matches(
    query: str,
) -> list[dict]:

    try:

        result = retrieve(
            query=query,
            top_k=8,
        )

        if not isinstance(
            result,
            list,
        ):
            return []

        return result

    except Exception as error:

        print(
            "[RAG RETRIEVAL ERROR]",
            repr(error),
        )

        return []


def get_best_document_score(
    matches: list[dict],
) -> float:

    scores: list[float] = []

    for match in matches:

        if not isinstance(
            match,
            dict,
        ):
            continue

        try:

            score = float(
                match.get(
                    "score",
                    0.0,
                )
            )

            scores.append(
                score
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

    if scores:
        return max(scores)

    return 0.0


# ============================================================
# RAG NODE
# ============================================================

def rag_node(
    state: AgentState,
) -> AgentState:

    state = update_web_url_state(
        state
    )

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    selected_document = safe_text(
        state.get(
            "selected_document",
            "",
        )
    )

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

            "knowledge_found": False,
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
        "Scope: ENTIRE KNOWLEDGE BASE",
    )

    # ========================================================
    # RETRIEVE
    # ========================================================

    matches = get_document_matches(
        query
    )

    best_score = get_best_document_score(
        matches
    )

    print(
        "Retrieved:",
        len(matches),
    )

    print(
        "Best score:",
        best_score,
    )

    # ========================================================
    # RELEVANCE CHECK
    # ========================================================

    if (
        not matches
        or best_score < RAG_RELEVANCE_THRESHOLD
    ):

        print(
            "[RAG] No sufficiently relevant KB result."
        )

        # IMPORTANT:
        #
        # Do NOT directly call web_node here.
        #
        # The graph.py conditional edge:
        #
        # rag -> web
        #
        # will handle the fallback.
        #
        # This prevents the web node from running twice.

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": [],

            "rag_found": False,

            "knowledge_found": False,

            "relevance_score": best_score,

            "fallback_to_web": True,

            "fallback_reason": (
                "No sufficiently relevant "
                "knowledge-base information."
            ),
        }

    # ========================================================
    # DOCUMENT RAG
    # ========================================================

    try:

        result = document_rag(
            query=query,
            selected_document=selected_document,
            history=history,
            documents=matches,
        )

    except Exception as error:

        print(
            "[DOCUMENT RAG ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": matches,

            "rag_found": False,

            "knowledge_found": False,

            "relevance_score": best_score,

            "fallback_to_web": True,

            "fallback_reason": (
                "Document answer generation failed."
            ),

            "error": str(error),
        }

    # ========================================================
    # VALIDATE RESULT
    # ========================================================

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": matches,

            "rag_found": False,

            "knowledge_found": False,

            "relevance_score": best_score,

            "fallback_to_web": True,

            "fallback_reason": (
                "Invalid document RAG result."
            ),
        }

    # ========================================================
    # EXTRACT
    # ========================================================

    answer = safe_text(
        result.get(
            "answer",
            "",
        )
    )

    relevant = bool(
        result.get(
            "relevant",
            False,
        )
    )

    sources = result.get(
        "sources",
        [],
    )

    if not isinstance(
        sources,
        list,
    ):
        sources = matches

    # ========================================================
    # NOT SUFFICIENT
    # ========================================================

    if (
        not relevant
        or not answer
    ):

        print(
            "[RAG] Retrieved chunks were not sufficient."
        )

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": sources,

            "relevance_score": best_score,

            "rag_found": False,

            "knowledge_found": False,

            "fallback_to_web": True,

            "fallback_reason": (
                "Knowledge-base retrieval was "
                "not sufficient to answer."
            ),
        }

    # ========================================================
    # SUCCESS
    # ========================================================

    print(
        "[RAG] SUCCESS"
    )

    return {
        **state,

        "route": "rag",

        "answer": answer,

        "sources": sources,

        "selected_document": selected_document,

        "document_context": bool(
            selected_document
        ),

        "relevance_score": best_score,

        "rag_found": True,

        "knowledge_found": True,

        "fallback_to_web": False,
    }


# ============================================================
# GENERAL NODE
# ============================================================

def general_node(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    history = safe_history(
        state
    )

    prompt = f"""
You are a helpful AI assistant.

Conversation:
{build_history_text(history)}

User:
{query}

Respond naturally and appropriately.

For greetings, respond conversationally.
For thanks, respond naturally.
For normal questions, answer directly.

Do not pretend to have searched the web.
Do not mention internal routing.
"""

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[GENERAL LLM ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "general",

            "answer": (
                "I'm having trouble generating a response "
                "right now. Please try again in a moment."
            ),

            "sources": [],

            "llm_error": str(error),
        }

    return {
        **state,

        "route": "general",

        "answer": safe_text(
            answer
        ),

        "sources": [],
    }


# ============================================================
# GREETING NODE
# ============================================================

def greeting_node(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    history = safe_history(
        state
    )

    prompt = f"""
You are a friendly conversational AI assistant.

Conversation:
{build_history_text(history)}

User:
{query}

Respond naturally to what the user said.

Do not use a fixed greeting template.
Do not assume the user said a specific greeting.
Understand the meaning and tone of the message.

Keep a simple greeting conversational and concise.
"""

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[GREETING LLM ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "greeting",

            "answer": (
                "I'm having trouble responding "
                "right now. Please try again."
            ),

            "sources": [],

            "llm_error": str(error),
        }

    return {
        **state,

        "route": "greeting",

        "answer": safe_text(
            answer
        ),

        "sources": [],
    }


# ============================================================
# WEB SEARCH NODE
# ============================================================

def web_node(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    if not query:

        return {
            **state,

            "route": "web",

            "answer": "",

            "sources": [],
        }

    print(
        "\n================ WEB SEARCH ================"
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

    except Exception as error:

        print(
            "[WEB SEARCH ERROR]",
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

            "error": str(error),
        }

    # ========================================================
    # INVALID RESULT
    # ========================================================

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "web",

            "answer": safe_text(
                result
            ),

            "sources": [],
        }

    # ========================================================
    # RESULT
    # ========================================================

    answer = safe_text(
        result.get(
            "answer",
            "",
        )
    )

    sources = result.get(
        "sources",
        [],
    )

    if not isinstance(
        sources,
        list,
    ):
        sources = []

    # ========================================================
    # SEARCH TOOL ALREADY GENERATED ANSWER
    # ========================================================

    if answer:

        return {
            **state,

            "route": "web",

            "answer": answer,

            "sources": sources,

            "web_context": False,
        }

    # ========================================================
    # BUILD SEARCH CONTEXT
    # ========================================================

    source_parts: list[str] = []

    for index, source in enumerate(
        sources[:5],
        start=1,
    ):

        if not isinstance(
            source,
            dict,
        ):
            continue

        title = safe_text(
            source.get(
                "title",
                "",
            )
        )

        content = safe_text(
            source.get(
                "snippet",
                source.get(
                    "content",
                    source.get(
                        "text",
                        "",
                    ),
                ),
            )
        )

        url = safe_text(
            source.get(
                "url",
                source.get(
                    "link",
                    "",
                ),
            )
        )

        source_parts.append(
            f"""
SOURCE {index}

TITLE:
{title}

CONTENT:
{content}

URL:
{url}
"""
        )

    # ========================================================
    # NO RESULTS
    # ========================================================

    if not source_parts:

        return {
            **state,

            "route": "web",

            "answer": (
                "I couldn't find useful web results "
                "for that question."
            ),

            "sources": [],
        }

    # ========================================================
    # SYNTHESIS
    # ========================================================

    prompt = f"""
Answer the user's question using ONLY the supplied web
search results.

USER QUESTION:
{query}

WEB RESULTS:
{"".join(source_parts)}

Rules:

- Do not invent facts.
- Do not use unsupported information.
- Give a direct answer.
- Do not mention internal routing.
"""

    try:

        generated = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[WEB SYNTHESIS ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "web",

            "answer": (
                "I found web results, but I couldn't "
                "generate the answer right now."
            ),

            "sources": sources,

            "llm_error": str(error),
        }

    return {
        **state,

        "route": "web",

        "answer": safe_text(
            generated
        ),

        "sources": sources,

        "web_context": False,
    }


# ============================================================
# WEB RAG NODE
# ============================================================

def web_rag_node(
    state: AgentState,
) -> AgentState:

    state = update_web_url_state(
        state
    )

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    history = safe_history(
        state
    )

    active_url = resolve_active_web_url(
        state
    )

    print(
        "\n================ WEB RAG NODE ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Active URL:",
        active_url or "NONE",
    )

    # ========================================================
    # NO URL
    # ========================================================

    if not active_url:

        print(
            "[WEB RAG] No active URL."
        )

        return web_node(
            {
                **state,

                "route": "web",

                "web_context": False,

                "fallback_to_web": True,
            }
        )

    # ========================================================
    # WEB RAG
    # ========================================================

    try:

        from app.rag.web_rag import (
            web_rag,
        )

        result = web_rag(
            query=query,
            url=active_url,
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
                "I couldn't retrieve the webpage "
                "information right now."
            ),

            "sources": [],

            "web_context": True,

            "web_url": active_url,

            "active_web_url": active_url,

            "error": str(error),
        }

    # ========================================================
    # INVALID RESULT
    # ========================================================

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "I couldn't generate a response "
                "from the webpage."
            ),

            "sources": [],

            "web_url": active_url,

            "active_web_url": active_url,
        }

    # ========================================================
    # EXTRACT
    # ========================================================

    answer = safe_text(
        result.get(
            "answer",
            "",
        )
    )

    sources = result.get(
        "sources",
        [],
    )

    if not isinstance(
        sources,
        list,
    ):
        sources = []

    url = safe_text(
        result.get(
            "url",
            active_url,
        )
    )

    if not url:
        url = active_url

    relevant = bool(
        result.get(
            "relevant",
            False,
        )
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

    # ========================================================
    # FAILED
    # ========================================================

    if (
        not relevant
        or not answer
    ):

        print(
            "[WEB RAG] No sufficient answer."
        )

        return web_node(
            {
                **state,

                "route": "web",

                "web_url": url,

                "active_web_url": url,

                "web_context": True,

                "sources": sources,

                "fallback_to_web": True,

                "fallback_reason": (
                    "Stored webpage did not contain "
                    "sufficient information."
                ),
            }
        )

    # ========================================================
    # SUCCESS
    # ========================================================

    return {
        **state,

        "route": "web_rag",

        "answer": answer,

        "sources": sources,

        "web_url": url,

        "active_web_url": url,

        "web_context": True,

        "web_title": safe_text(
            result.get(
                "title",
                "",
            )
        ),

        "web_scraper": safe_text(
            result.get(
                "scraping_method",
                "",
            )
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

        "web_relevance_score": (
            result.get(
                "best_score",
                0.0,
            )
            or 0.0
        ),
    }


# ============================================================
# WEATHER NODE
# ============================================================

def weather_node(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    try:

        from app.tools.weather_tool import (
            get_weather,
        )

        location_prompt = f"""
Extract the location from this weather request.

Return only the location name.

Question:
{query}
"""

        city = safe_text(
            llm.generate(
                location_prompt
            )
        )

        city = city.strip(
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

                "answer": safe_text(
                    result
                ),

                "sources": [],
            }

        return {
            **state,

            "route": "weather",

            "answer": safe_text(
                result.get(
                    "answer",
                    "",
                )
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
                "I couldn't retrieve the weather "
                "right now."
            ),

            "sources": [],

            "error": str(error),
        }


# ============================================================
# OCR NODE
# ============================================================

def ocr_node(
    state: AgentState,
) -> AgentState:

    query = safe_text(
        state.get(
            "query",
            "",
        )
    )

    ocr_text = safe_text(
        state.get(
            "ocr_text",
            "",
        )
    )

    history = safe_history(
        state
    )

    if not ocr_text:

        return {
            **state,

            "route": "ocr",

            "answer": (
                "No OCR text is available."
            ),

            "sources": [],
        }

    prompt = f"""
Answer the user's question using ONLY the OCR text.

OCR TEXT:
{ocr_text}

CONVERSATION:
{build_history_text(history)}

QUESTION:
{query}

If the answer is not present in the OCR text,
say that it cannot be found in the uploaded image.
"""

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[OCR ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "ocr",

            "answer": (
                "I couldn't answer from the uploaded "
                "image right now."
            ),

            "sources": [],

            "error": str(error),
        }

    return {
        **state,

        "route": "ocr",

        "answer": safe_text(
            answer
        ),

        "sources": [],
    }