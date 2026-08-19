from __future__ import annotations

from typing import TypedDict, Any


class AgentState(TypedDict, total=False):

    # Current request
    query: str

    # Conversation
    history: list[dict]

    # Output
    answer: str
    sources: list[dict]
    route: str

    # PDF / Knowledge Base
    selected_document: str
    document_context: bool

    # Web RAG
    web_url: str
    web_context: bool

    # OCR
    ocr_text: str

    # RAG metadata
    relevance_score: float
    rag_found: bool

    # Web metadata
    web_title: str
    web_scraper: str
    web_chunks: int
    web_indexed: bool
    web_relevance_score: float

    # Misc
    fallback_reason: str
    error: str
    input_type: str
    audio: Any