from __future__ import annotations

import traceback
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.graph import agent


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# ============================================================
# SAFE STRING HELPER
# ============================================================

def safe_str(value: Any) -> str:
    """
    Safely convert any value into a stripped string.

    Handles:
    - None
    - strings
    - numbers
    - accidental one-item tuples
    - accidental multi-item tuples
    """

    if value is None:
        return ""

    # Handle accidental tuple values.
    if isinstance(value, tuple):

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
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    message: str = Field(
        ...,
        min_length=1,
    )

    # --------------------------------------------------------
    # PDF DOCUMENT
    # --------------------------------------------------------

    selected_document: str = ""

    document_context: bool = False

    # --------------------------------------------------------
    # WEB RAG
    # --------------------------------------------------------

    web_url: str = ""

    web_context: bool = False

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    ocr_text: str = ""

    # --------------------------------------------------------
    # CONVERSATION HISTORY
    # --------------------------------------------------------

    history: list[dict] = Field(
        default_factory=list
    )


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post("")
async def chat(
    request: ChatRequest,
):

    # ========================================================
    # CLEAN INPUT
    # ========================================================

    query = safe_str(
        request.message
    )

    selected_document = safe_str(
        request.selected_document
    )

    web_url = safe_str(
        request.web_url
    )

    ocr_text = safe_str(
        request.ocr_text
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # ========================================================
    # CONTEXT FLAGS
    # ========================================================

    document_context = bool(
        selected_document
    )

    web_context = bool(
        web_url
    )

    # ========================================================
    # HISTORY
    # ========================================================

    history = request.history

    if not isinstance(
        history,
        list,
    ):
        history = []

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n================ API CHAT ================"
    )

    print(
        "Message:",
        query,
    )

    print(
        "Message type:",
        type(query).__name__,
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    print(
        "Document context:",
        document_context,
    )

    print(
        "Web URL:",
        web_url or "NONE",
    )

    print(
        "Web context:",
        web_context,
    )

    print(
        "OCR available:",
        bool(ocr_text),
    )

    print(
        "History messages:",
        len(history),
    )

    print(
        "=========================================="
    )

    # ========================================================
    # BUILD AGENT STATE
    # ========================================================

    state = {

        "query": query,

        "selected_document": selected_document,

        "document_context": document_context,

        "web_url": web_url,

        "web_context": web_context,

        "ocr_text": ocr_text,

        "history": history,

        "answer": "",

        "sources": [],

        "route": "",
    }

    # ========================================================
    # RUN AGENT
    # ========================================================

    try:

        result = agent.invoke(
            state
        )

    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "CHAT / AGENT ERROR"
        )

        print(
            "Error type:",
            type(error).__name__,
        )

        print(
            "Error:",
            repr(error),
        )

        print(
            "\nFULL TRACEBACK:"
        )

        traceback.print_exc()

        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent failed to process the request: "
                f"{type(error).__name__}: {error}"
            ),
        )

    # ========================================================
    # VALIDATE RESULT
    # ========================================================

    if not isinstance(
        result,
        dict,
    ):

        raise HTTPException(
            status_code=500,
            detail="Agent returned an invalid response.",
        )

    # ========================================================
    # EXTRACT RESULT
    # ========================================================

    answer = safe_str(
        result.get(
            "answer",
            "",
        )
    )

    route = safe_str(
        result.get(
            "route",
            "general",
        )
    ).lower()

    result_selected_document = safe_str(
        result.get(
            "selected_document",
            selected_document,
        )
    )

    result_web_url = safe_str(
        result.get(
            "web_url",
            web_url,
        )
    )

    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    sources = result.get(
        "sources",
        [],
    )

    if sources is None:
        sources = []

    if not isinstance(
        sources,
        list,
    ):
        sources = [sources]

    # --------------------------------------------------------
    # CONTEXT FLAGS
    # --------------------------------------------------------

    result_document_context = bool(
        result.get(
            "document_context",
            document_context,
        )
    )

    result_web_context = bool(
        result.get(
            "web_context",
            web_context,
        )
    )

    # ========================================================
    # DEBUG RESULT
    # ========================================================

    print(
        "\n================ AGENT RESULT ================"
    )

    print(
        "Answer:",
        answer,
    )

    print(
        "Answer type:",
        type(answer).__name__,
    )

    print(
        "Route:",
        route,
    )

    print(
        "Route type:",
        type(route).__name__,
    )

    print(
        "Selected document:",
        result_selected_document or "NONE",
    )

    print(
        "Web URL:",
        result_web_url or "NONE",
    )

    print(
        "Sources:",
        len(sources),
    )

    print(
        "================================================\n"
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "answer": answer,

        "route": route,

        "sources": sources,

        "selected_document": (
            result_selected_document
        ),

        "web_url": (
            result_web_url
        ),

        "document_context": (
            result_document_context
        ),

        "web_context": (
            result_web_context
        ),
    }