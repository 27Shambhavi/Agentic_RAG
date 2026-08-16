from __future__ import annotations

from app.agents.state import AgentState

from app.rag.document_rag import document_rag
from app.rag.retriever import retrieve

from app.llm.gemini import llm


# =========================================================
# CONFIGURATION
# =========================================================

RAG_RELEVANCE_THRESHOLD = 0.15


# =========================================================
# SAFE HISTORY
# =========================================================

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


# =========================================================
# HISTORY TEXT
# =========================================================

def build_history_text(
    history: list[dict],
) -> str:

    history_parts = []

    for message in history[-5:]:

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
        ).strip()

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if content:

            history_parts.append(
                f"{role.upper()}: {content}"
            )

    if not history_parts:

        return "No previous conversation."

    return "\n".join(
        history_parts
    )


# =========================================================
# DOCUMENT RETRIEVAL
# =========================================================
#
# IMPORTANT:
#
# This is the ONLY retrieval call for PDF RAG.
#
# document_rag() receives these already-retrieved
# documents and DOES NOT retrieve again.
#
# =========================================================

def get_document_matches(
    query: str,
    selected_document: str,
) -> list[dict]:

    if (
        not query
        or not selected_document
    ):
        return []

    try:

        matches = retrieve(
            query=query,
            top_k=5,
            selected_document=selected_document,
        )

        if not matches:

            return []

        return matches

    except Exception as error:

        print(
            "[RAG RETRIEVAL ERROR]",
            repr(error),
        )

        return []


# =========================================================
# BEST DOCUMENT SCORE
# =========================================================

def get_best_document_score(
    matches,
) -> float:

    best_score = 0.0

    for match in matches or []:

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

            best_score = max(
                best_score,
                score,
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

    return best_score


# =========================================================
# PDF / DOCUMENT RAG NODE
# =========================================================
#
# IMPORTANT ARCHITECTURE:
#
# PDF RAG NEVER falls back to normal Web Search.
#
# If a PDF is selected:
#
#     selected PDF
#          ↓
#       retrieve
#          ↓
#      relevance
#          ↓
#    document_rag
#          ↓
#        LLM
#
# Web Search is a completely separate route.
#
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

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,

            "route": "rag",

            "answer": "",

            "sources": [],

            "relevance_score": 0.0,
        }

    # =====================================================
    # NO DOCUMENT
    # =====================================================

    if not selected_document:

        print(
            "[RAG] No selected document."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "Please select a PDF document first."
            ),

            "sources": [],

            "document_context": False,

            "relevance_score": 0.0,
        }

    # =====================================================
    # START LOGGING
    # =====================================================

    print(
        "\n================ RAG NODE ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected document:",
        selected_document,
    )

    print(
        "RAG threshold:",
        RAG_RELEVANCE_THRESHOLD,
    )

    # =====================================================
    # RETRIEVE
    # =====================================================

    matches = get_document_matches(
        query=query,
        selected_document=selected_document,
    )

    best_score = get_best_document_score(
        matches
    )

    print(
        "Retrieved chunks:",
        len(matches),
    )

    print(
        "Best relevance score:",
        best_score,
    )

    # =====================================================
    # NO MATCHES
    # =====================================================
    #
    # IMPORTANT:
    #
    # DO NOT CALL web_node().
    #
    # =====================================================

    if not matches:

        print(
            "[RAG] No chunks found for selected document."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I couldn't find relevant information "
                "in the selected document."
            ),

            "sources": [],

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": 0.0,
        }

    # =====================================================
    # RELEVANCE GATE
    # =====================================================
    #
    # ONLY ONE PDF RELEVANCE GATE.
    #
    # document_rag() does NOT apply another threshold.
    #
    # =====================================================

    if best_score < RAG_RELEVANCE_THRESHOLD:

        print(
            "[RAG] Relevance below threshold."
        )

        print(
            f"[RAG] {best_score:.4f} < "
            f"{RAG_RELEVANCE_THRESHOLD:.4f}"
        )

        print(
            "[RAG] Staying in PDF RAG."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I couldn't find enough relevant information "
                "in the selected document to answer this question."
            ),

            "sources": matches,

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": best_score,
        }

    # =====================================================
    # RELEVANT DOCUMENT
    # =====================================================

    print(
        "[RAG] Relevant document chunks found."
    )

    print(
        "[RAG] Passing retrieved chunks to document_rag()."
    )

    # =====================================================
    # DOCUMENT RAG GENERATION
    # =====================================================
    #
    # IMPORTANT:
    #
    # Pass `matches` directly.
    #
    # document_rag() must NOT call retrieve() again.
    #
    # =====================================================

    try:

        result = document_rag(
            query=query,

            selected_document=selected_document,

            history=history,

            documents=matches,
        )

    except Exception as error:

        print(
            "[RAG ANSWER ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I found relevant information in the "
                "selected document, but I couldn't "
                "generate the answer right now."
            ),

            "sources": matches,

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": best_score,
        }

    # =====================================================
    # INVALID RESULT
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        print(
            "[RAG] Invalid document_rag result."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I found relevant information in the "
                "selected document, but couldn't "
                "generate a valid answer."
            ),

            "sources": matches,

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": best_score,
        }

    # =====================================================
    # ANSWER
    # =====================================================

    answer = (
        result.get(
            "answer",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # SOURCES
    # =====================================================

    sources = (
        result.get(
            "sources",
            [],
        )
        or []
    )

    if not sources:

        sources = matches

    # =====================================================
    # DOCUMENT RAG RELEVANCE
    # =====================================================
    #
    # document_rag() should normally return relevant=True
    # because rag_node() already passed the relevance gate.
    #
    # We do NOT route to Web if it says False.
    #
    # =====================================================

    relevant = result.get(
        "relevant",
        True,
    )

    if relevant is False:

        print(
            "[RAG] document_rag reported insufficient content."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I couldn't find enough information "
                "in the selected document to answer "
                "this question."
            ),

            "sources": sources or matches,

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": best_score,
        }

    # =====================================================
    # EMPTY ANSWER
    # =====================================================

    if not answer:

        print(
            "[RAG] Empty document answer."
        )

        return {
            **state,

            "route": "rag",

            "answer": (
                "I found relevant information in the "
                "selected document, but couldn't generate "
                "an answer right now."
            ),

            "sources": sources,

            "selected_document": selected_document,

            "document_context": True,

            "relevance_score": best_score,
        }

    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        "[RAG] SUCCESS"
    )

    print(
        "RAG relevance:",
        best_score,
    )

    print(
        "RAG sources:",
        len(sources),
    )

    print(
        "==========================================\n"
    )

    return {
        **state,

        "route": "rag",

        "answer": answer,

        "sources": sources,

        "selected_document": selected_document,

        "document_context": True,

        "relevance_score": best_score,
    }


# =========================================================
# GENERAL AI NODE
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

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,

            "route": "general",

            "answer": "",

            "sources": [],
        }

    history_text = build_history_text(
        history
    )

    # =====================================================
    # GENERAL PROMPT
    # =====================================================

    prompt = f"""
You are a helpful general-purpose AI assistant.

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{query}

Answer the user's question directly and naturally.

Use your own general knowledge.

Do not mention:
- RAG
- Pinecone
- routing
- internal tools
- system architecture
- document retrieval
"""

    try:

        print(
            "\n================ GENERAL LLM ================"
        )

        print(
            "Query:",
            query,
        )

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

        if answer:

            print(
                "[GENERAL] LLM SUCCESS"
            )

            print(
                "=============================================\n"
            )

            return {
                **state,

                "route": "general",

                "answer": answer,

                "sources": [],
            }

    except Exception as error:

        print(
            "[GENERAL LLM ERROR]",
            repr(error),
        )

    # =====================================================
    # GENERAL LLM FAILED
    # =====================================================
    #
    # This fallback is still normal Web Search because
    # there is NO active PDF context here.
    #
    # =====================================================

    print(
        "[GENERAL] LLM failed -> WEB search."
    )

    return web_node(
        {
            **state,

            "route": "web",

            "fallback_reason": (
                "General LLM failed."
            ),
        }
    )


# =========================================================
# GREETING NODE
# =========================================================

def greeting_node(
    state: AgentState,
) -> AgentState:

    return {
        **state,

        "route": "greeting",

        "answer": (
            "Hello! 👋 How can I help you today?"
        ),

        "sources": [],
    }


# =========================================================
# NORMAL WEB SEARCH NODE
# =========================================================
#
# This is DIFFERENT from Web RAG.
#
# Normal Web Search:
#
# user question
#      ↓
# search engine
#      ↓
# search results
#      ↓
# LLM
#
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

        # =================================================
        # INVALID RESULT
        # =================================================

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

        # =================================================
        # ANSWER
        # =================================================

        answer = (
            result.get(
                "answer",
                "",
            )
            or ""
        ).strip()

        # =================================================
        # SOURCES
        # =================================================

        sources = (
            result.get(
                "sources",
                [],
            )
            or []
        )

        print(
            "Web sources:",
            len(sources),
        )

        # =================================================
        # DIRECT ANSWER
        # =================================================

        if answer:

            return {
                **state,

                "route": "web",

                "answer": answer,

                "sources": sources,
            }

        # =================================================
        # SOURCE-ONLY FALLBACK
        # =================================================

        if sources:

            source_text = []

            for index, source in enumerate(
                sources[:5],
                start=1,
            ):

                if not isinstance(
                    source,
                    dict,
                ):
                    continue

                title = str(
                    source.get(
                        "title",
                        "",
                    )
                )

                content = str(
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

                url = str(
                    source.get(
                        "url",
                        source.get(
                            "link",
                            "",
                        ),
                    )
                )

                source_text.append(
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

            combined_sources = "\n".join(
                source_text
            )

            synthesis_prompt = f"""
You are a helpful AI assistant.

USER QUESTION:
{query}

WEB SEARCH RESULTS:
{combined_sources}

Answer the user's question using ONLY
the information contained in the web search results.

Rules:

1. Give a direct answer.
2. Use the search results as evidence.
3. Do not invent unsupported facts.
4. If the results are insufficient, say so.
5. Do not mention internal routing.
6. Do not mention RAG or Pinecone.
"""

            try:

                generated_answer = llm.generate(
                    synthesis_prompt
                )

                generated_answer = (
                    generated_answer or ""
                ).strip()

                if generated_answer:

                    return {
                        **state,

                        "route": "web",

                        "answer": generated_answer,

                        "sources": sources,
                    }

            except Exception as error:

                print(
                    "[WEB FALLBACK LLM ERROR]",
                    repr(error),
                )

        # =================================================
        # NO ANSWER
        # =================================================

        return {
            **state,

            "route": "web",

            "answer": (
                "I found web results, but I "
                "couldn't generate a reliable answer "
                "from them right now."
            ),

            "sources": sources,
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
                "I couldn't perform the web "
                "search right now."
            ),

            "sources": [],
        }


# =========================================================
# WEB RAG NODE
# =========================================================
#
# USER URL
#      ↓
# WEB RAG
#
# This remains completely separate from PDF RAG.
#
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

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,

            "route": "web_rag",

            "answer": "",

            "sources": [],
        }

    # =====================================================
    # URL MISSING
    # =====================================================

    if not web_url:

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "Please provide a webpage URL "
                "that you want me to analyze."
            ),

            "sources": [],

            "web_context": False,
        }

    print(
        "\n================ WEB RAG NODE ================"
    )

    print(
        "URL:",
        web_url,
    )

    print(
        "Question:",
        query,
    )

    # =====================================================
    # IMPORT WEB RAG
    # =====================================================

    try:

        from app.rag.web_rag import (
            web_rag,
        )

    except Exception as error:

        print(
            "[WEB RAG IMPORT ERROR]",
            repr(error),
        )

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "Web RAG is not configured correctly."
            ),

            "sources": [],

            "web_url": web_url,

            "web_context": False,
        }

    # =====================================================
    # RUN WEB RAG
    # =====================================================

    try:

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
                "that webpage right now."
            ),

            "sources": [],

            "web_url": web_url,

            "web_context": False,
        }

    # =====================================================
    # INVALID RESULT
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "The webpage was retrieved, "
                "but I couldn't generate a reliable answer."
            ),

            "sources": [],

            "web_url": web_url,

            "web_context": True,
        }

    # =====================================================
    # RESULT
    # =====================================================

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

    # =====================================================
    # WEB METADATA
    # =====================================================

    title = (
        result.get(
            "title",
            "",
        )
        or ""
    )

    scraping_method = (
        result.get(
            "scraping_method",
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

    chunks = index_result.get(
        "chunks",
        0,
    )

    indexed = (
        index_result.get(
            "status",
            "",
        )
        == "indexed"
    )

    # =====================================================
    # LOGGING
    # =====================================================

    print(
        "Title:",
        title,
    )

    print(
        "Scraping method:",
        scraping_method or "unknown",
    )

    print(
        "Chunks:",
        chunks,
    )

    print(
        "Best score:",
        best_score,
    )

    print(
        "Sources:",
        len(sources),
    )

    # =====================================================
    # WEB METADATA
    # =====================================================

    web_metadata = {

        "web_url": web_url,

        "web_context": True,

        "web_title": title,

        "web_scraper": scraping_method,

        "web_chunks": chunks,

        "web_indexed": indexed,

        "web_relevance_score": best_score,
    }

    # =====================================================
    # WEB RAG RELEVANCE
    # =====================================================

    relevant = result.get(
        "relevant",
        False,
    )

    # =====================================================
    # IMPORTANT:
    #
    # User explicitly supplied a URL.
    #
    # Never turn Web RAG into normal Web Search.
    # =====================================================

    if relevant is False:

        insufficient_answer = (
            answer
            or
            "I could not find enough relevant "
            "information on the provided webpage "
            "to answer this question."
        )

        return {
            **state,

            "route": "web_rag",

            "answer": insufficient_answer,

            "sources": sources,

            **web_metadata,
        }

    # =====================================================
    # EMPTY ANSWER
    # =====================================================

    if not answer:

        return {
            **state,

            "route": "web_rag",

            "answer": (
                "I retrieved the webpage, "
                "but couldn't find enough information "
                "to answer your question."
            ),

            "sources": sources,

            **web_metadata,
        }

    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        "[WEB RAG] SUCCESS"
    )

    print(
        "==============================================\n"
    )

    return {
        **state,

        "route": "web_rag",

        "answer": answer,

        "sources": sources,

        **web_metadata,
    }


# =========================================================
# WEATHER NODE
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

    if not query:

        return {
            **state,

            "route": "weather",

            "answer": "",

            "sources": [],
        }

    try:

        from app.tools.weather_tool import (
            get_weather,
        )

        # =================================================
        # EXTRACT LOCATION
        # =================================================

        location_prompt = f"""
Extract the city or location from this weather question.

Return ONLY the city or location name.

QUESTION:
{query}
"""

        city = llm.generate(
            location_prompt
        )

        city = (
            city
            .replace(
                '"',
                "",
            )
            .replace(
                "'",
                "",
            )
            .strip()
        )

        if not city:

            return {
                **state,

                "route": "weather",

                "answer": (
                    "Please specify a city or "
                    "location for the weather request."
                ),

                "sources": [],
            }

        # =================================================
        # GET WEATHER
        # =================================================

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
            "[WEATHER NODE ERROR]",
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
        }


# =========================================================
# OCR NODE
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

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,

            "route": "ocr",

            "answer": "",

            "sources": [],
        }

    # =====================================================
    # NO OCR
    # =====================================================

    if not ocr_text:

        return {
            **state,

            "route": "ocr",

            "answer": (
                "No image text is available. "
                "Please upload an image first."
            ),

            "sources": [],
        }

    history_text = build_history_text(
        history
    )

    # =====================================================
    # OCR PROMPT
    # =====================================================

    prompt = f"""
You are answering a question about an uploaded image.

IMAGE OCR TEXT:
{ocr_text}

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{query}

Answer ONLY using the OCR text.

If the answer is not present in the OCR text,
say that it cannot be found in the image.

Do not use outside knowledge.
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
            "I couldn't generate an answer "
            "from the image."
        )

    return {
        **state,

        "route": "ocr",

        "answer": answer,

        "sources": [],
    }


# =========================================================
# ROUTE EXECUTION
# =========================================================
#
# This function is kept for compatibility if your graph
# or another module imports it.
#
# =========================================================

def route_node(
    state: AgentState,
) -> AgentState:

    route = (
        state.get(
            "route",
            "general",
        )
        or "general"
    ).strip().lower()

    print(
        "[ROUTE NODE] Executing:",
        route,
    )

    # =====================================================
    # PDF RAG
    # =====================================================

    if route == "rag":

        return rag_node(
            state
        )

    # =====================================================
    # WEB RAG
    # =====================================================

    if route == "web_rag":

        return web_rag_node(
            state
        )

    # =====================================================
    # NORMAL WEB
    # =====================================================

    if route == "web":

        return web_node(
            state
        )

    # =====================================================
    # WEATHER
    # =====================================================

    if route == "weather":

        return weather_node(
            state
        )

    # =====================================================
    # OCR
    # =====================================================

    if route == "ocr":

        return ocr_node(
            state
        )

    # =====================================================
    # GREETING
    # =====================================================

    if route == "greeting":

        return greeting_node(
            state
        )

    # =====================================================
    # GENERAL
    # =====================================================

    return general_node(
        state
    )