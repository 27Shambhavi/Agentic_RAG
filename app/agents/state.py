from typing import TypedDict


class AgentState(TypedDict, total=False):

    # =====================================================
    # USER QUERY
    # =====================================================

    query: str

    # =====================================================
    # PDF RAG
    # =====================================================

    selected_document: str

    document_context: bool

    # =====================================================
    # WEB RAG
    #
    # URL supplied by the user.
    #
    # Example:
    # https://example.com/article
    # =====================================================

    web_url: str

    web_context: bool

    # =====================================================
    # OCR
    # =====================================================

    ocr_text: str

    # =====================================================
    # CONVERSATION HISTORY
    # =====================================================

    history: list[dict]

    # =====================================================
    # AGENT OUTPUT
    # =====================================================

    answer: str

    sources: list[dict]

    route: str

    # =====================================================
    # OPTIONAL WEB RAG DATA
    #
    # These fields will be populated when a URL is
    # scraped and indexed.
    # =====================================================

    web_title: str

    web_chunks: list[dict]

    web_sources: list[dict]