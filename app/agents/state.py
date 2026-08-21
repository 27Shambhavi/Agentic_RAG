from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):

    # ========================================================
    # CURRENT REQUEST
    # ========================================================

    query: str

    # ========================================================
    # CONVERSATION
    # ========================================================

    history: list[dict]

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    answer: str
    sources: list[dict]
    route: str

    # ========================================================
    # DOCUMENT KNOWLEDGE BASE
    # ========================================================

    selected_document: str
    document_context: bool

    relevance_score: float
    rag_found: bool
    knowledge_found: bool

    # ========================================================
    # WEB CONTEXT
    # ========================================================

    web_url: str

    # Persisted/active URL context.
    active_web_url: str

    # URLs encountered during conversation.
    web_urls: list[str]

    web_context: bool
    web_title: str
    web_scraper: str
    web_chunks: int
    web_indexed: bool
    web_relevance_score: float

    # ========================================================
    # OCR
    # ========================================================

    ocr_text: str

    # ========================================================
    # INPUT
    # ========================================================

    input_type: str
    audio: Any

    # ========================================================
    # CONTROL / DEBUG
    # ========================================================

    fallback_reason: str
    fallback_to_web: bool
    llm_error: str
    error: str