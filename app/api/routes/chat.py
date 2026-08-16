# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field

# from app.agents.graph import agent


# # =========================================================
# # ROUTER
# # =========================================================

# router = APIRouter(
#     prefix="/api/chat",
#     tags=["Chat"],
# )


# # =========================================================
# # REQUEST MODEL
# # =========================================================

# class ChatRequest(BaseModel):

#     # -----------------------------------------------------
#     # USER MESSAGE
#     # -----------------------------------------------------

#     message: str = Field(
#         ...,
#         min_length=1,
#     )

#     # -----------------------------------------------------
#     # ACTIVE DOCUMENT
#     # -----------------------------------------------------

#     selected_document: str = ""

#     # -----------------------------------------------------
#     # DOCUMENT CONTEXT
#     #
#     # This tells the backend that a document is currently
#     # selected/active.
#     #
#     # IMPORTANT:
#     # It does NOT force every question to use RAG.
#     # The supervisor/classifier decides the route.
#     # -----------------------------------------------------

#     document_context: bool = False

#     # -----------------------------------------------------
#     # OCR CONTEXT
#     #
#     # Extracted text from the currently processed image.
#     # This allows follow-up questions about an OCR image.
#     # -----------------------------------------------------

#     ocr_text: str = ""

#     # -----------------------------------------------------
#     # CONVERSATION HISTORY
#     #
#     # Used to preserve conversational context.
#     # -----------------------------------------------------

#     history: list[dict] = Field(
#         default_factory=list
#     )


# # =========================================================
# # CHAT ENDPOINT
# # =========================================================

# @router.post("")
# async def chat(
#     request: ChatRequest,
# ):

#     # =====================================================
#     # CLEAN INPUT
#     # =====================================================

#     query = request.message.strip()

#     selected_document = (
#         request.selected_document.strip()
#     )

#     ocr_text = (
#         request.ocr_text.strip()
#     )


#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not query:

#         raise HTTPException(
#             status_code=400,
#             detail="Message cannot be empty.",
#         )


#     # =====================================================
#     # BUILD AGENT STATE
#     # =====================================================

#     state = {

#         # -------------------------------------------------
#         # Current user question
#         # -------------------------------------------------

#         "query": query,


#         # -------------------------------------------------
#         # Active document
#         # -------------------------------------------------

#         "selected_document": (
#             selected_document
#         ),


#         # -------------------------------------------------
#         # Whether a document is active
#         # -------------------------------------------------

#         "document_context": (
#             request.document_context
#         ),


#         # -------------------------------------------------
#         # OCR context
#         # -------------------------------------------------

#         "ocr_text": (
#             ocr_text
#         ),


#         # -------------------------------------------------
#         # Conversation history
#         # -------------------------------------------------

#         "history": (
#             request.history
#         ),


#         # -------------------------------------------------
#         # Clean output fields
#         # -------------------------------------------------

#         "answer": "",

#         "sources": [],

#         "route": "",
#     }


#     # =====================================================
#     # RUN AGENT
#     # =====================================================

#     try:

#         result = agent.invoke(
#             state
#         )


#     except Exception as error:

#         print(
#             "\n========================================"
#         )

#         print(
#             "CHAT / AGENT ERROR"
#         )

#         print(
#             repr(error)
#         )

#         print(
#             "========================================\n"
#         )


#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Agent failed to process the request."
#             ),
#         )


#     # =====================================================
#     # SAFE RESPONSE
#     # =====================================================

#     if not isinstance(
#         result,
#         dict,
#     ):

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Agent returned an invalid response."
#             ),
#         )


#     # =====================================================
#     # RESPONSE
#     # =====================================================

#     return {

#         # -------------------------------------------------
#         # FINAL ANSWER
#         # -------------------------------------------------

#         "answer": result.get(
#             "answer",
#             "",
#         ),


#         # -------------------------------------------------
#         # ROUTE
#         #
#         # rag
#         # web
#         # general
#         # greeting
#         # -------------------------------------------------

#         "route": result.get(
#             "route",
#             "general",
#         ),


#         # -------------------------------------------------
#         # SOURCES
#         # -------------------------------------------------

#         "sources": result.get(
#             "sources",
#             [],
#         ),


#         # -------------------------------------------------
#         # ACTIVE DOCUMENT
#         # -------------------------------------------------

#         "selected_document": result.get(
#             "selected_document",
#             selected_document,
#         ),
#     }
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.graph import agent


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    # =====================================================
    # USER MESSAGE
    # =====================================================

    message: str = Field(
        ...,
        min_length=1,
    )

    # =====================================================
    # ACTIVE PDF DOCUMENT
    # =====================================================

    selected_document: str = ""

    document_context: bool = False

    # =====================================================
    # WEB RAG
    #
    # Example:
    #
    # web_url:
    # https://example.com/article
    #
    # web_context:
    # True
    #
    # This is different from the normal web-search tool.
    #
    # Web RAG:
    #
    # URL
    #   ↓
    # Scrape
    #   ↓
    # Clean
    #   ↓
    # Chunk
    #   ↓
    # Embed
    #   ↓
    # Pinecone
    #   ↓
    # Retrieve
    #   ↓
    # LLM
    # =====================================================

    web_url: str = ""

    web_context: bool = False

    # =====================================================
    # OCR
    # =====================================================

    ocr_text: str = ""

    # =====================================================
    # CONVERSATION HISTORY
    # =====================================================

    history: list[dict] = Field(
        default_factory=list
    )


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post("")
async def chat(
    request: ChatRequest,
):

    # =====================================================
    # CLEAN INPUT
    # =====================================================

    query = (
        request.message or ""
    ).strip()

    selected_document = (
        request.selected_document or ""
    ).strip()

    web_url = (
        request.web_url or ""
    ).strip()

    ocr_text = (
        request.ocr_text or ""
    ).strip()

    # =====================================================
    # VALIDATION
    # =====================================================

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # =====================================================
    # DOCUMENT CONTEXT
    #
    # Keep backend state consistent.
    #
    # If a document name is supplied, document_context
    # should be considered active.
    # =====================================================

    document_context = bool(
        selected_document
    )

    # =====================================================
    # WEB CONTEXT
    #
    # If a URL is supplied, web context is active.
    #
    # This does NOT mean normal web search.
    #
    # It means:
    #
    # URL -> Web RAG
    # =====================================================

    web_context = bool(
        web_url
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n================ API CHAT ================"
    )

    print(
        "Message:",
        query,
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
        len(request.history),
    )

    print(
        "=========================================="
    )

    # =====================================================
    # BUILD AGENT STATE
    # =====================================================

    state = {

        # -------------------------------------------------
        # USER QUERY
        # -------------------------------------------------

        "query": query,

        # -------------------------------------------------
        # PDF RAG
        # -------------------------------------------------

        "selected_document": (
            selected_document
        ),

        "document_context": (
            document_context
        ),

        # -------------------------------------------------
        # WEB RAG
        # -------------------------------------------------

        "web_url": (
            web_url
        ),

        "web_context": (
            web_context
        ),

        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        "ocr_text": (
            ocr_text
        ),

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        "history": (
            request.history
        ),

        # -------------------------------------------------
        # OUTPUT FIELDS
        # -------------------------------------------------

        "answer": "",

        "sources": [],

        "route": "",

    }

    # =====================================================
    # RUN AGENT
    # =====================================================

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
            repr(error)
        )

        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent failed to process the request."
            ),
        )

    # =====================================================
    # VALIDATE AGENT RESULT
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent returned an invalid response."
            ),
        )

    # =====================================================
    # DEBUG RESULT
    # =====================================================

    print(
        "\n================ AGENT RESULT ================"
    )

    print(
        "Route:",
        result.get(
            "route",
            "general",
        ),
    )

    print(
        "Selected document:",
        result.get(
            "selected_document",
            selected_document,
        ),
    )

    print(
        "Web URL:",
        result.get(
            "web_url",
            web_url,
        ),
    )

    print(
        "Sources:",
        len(
            result.get(
                "sources",
                [],
            ) or []
        ),
    )

    print(
        "================================================\n"
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        # -------------------------------------------------
        # ANSWER
        # -------------------------------------------------

        "answer": (
            result.get(
                "answer",
                "",
            )
            or ""
        ),

        # -------------------------------------------------
        # ROUTE
        #
        # rag
        # web
        # web_rag
        # general
        # greeting
        # weather
        # ocr
        # -------------------------------------------------

        "route": (
            result.get(
                "route",
                "general",
            )
            or "general"
        ),

        # -------------------------------------------------
        # SOURCES
        # -------------------------------------------------

        "sources": (
            result.get(
                "sources",
                [],
            )
            or []
        ),

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        "selected_document": (
            result.get(
                "selected_document",
                selected_document,
            )
            or ""
        ),

        # -------------------------------------------------
        # WEB RAG URL
        # -------------------------------------------------

        "web_url": (
            result.get(
                "web_url",
                web_url,
            )
            or ""
        ),

        # -------------------------------------------------
        # CONTEXT FLAGS
        # -------------------------------------------------

        "document_context": (
            result.get(
                "document_context",
                document_context,
            )
        ),

        "web_context": (
            result.get(
                "web_context",
                web_context,
            )
        )
    }