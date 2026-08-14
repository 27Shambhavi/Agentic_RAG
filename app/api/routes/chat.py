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

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    message: str = Field(
        ...,
        min_length=1,
    )

    # -----------------------------------------------------
    # ACTIVE DOCUMENT
    # -----------------------------------------------------

    selected_document: str = ""

    # -----------------------------------------------------
    # DOCUMENT CONTEXT
    #
    # This tells the backend that a document is currently
    # selected/active.
    #
    # IMPORTANT:
    # It does NOT force every question to use RAG.
    # The supervisor/classifier decides the route.
    # -----------------------------------------------------

    document_context: bool = False

    # -----------------------------------------------------
    # OCR CONTEXT
    #
    # Extracted text from the currently processed image.
    # This allows follow-up questions about an OCR image.
    # -----------------------------------------------------

    ocr_text: str = ""

    # -----------------------------------------------------
    # CONVERSATION HISTORY
    #
    # Used to preserve conversational context.
    # -----------------------------------------------------

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

    query = request.message.strip()

    selected_document = (
        request.selected_document.strip()
    )

    ocr_text = (
        request.ocr_text.strip()
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )


    # =====================================================
    # BUILD AGENT STATE
    # =====================================================

    state = {

        # -------------------------------------------------
        # Current user question
        # -------------------------------------------------

        "query": query,


        # -------------------------------------------------
        # Active document
        # -------------------------------------------------

        "selected_document": (
            selected_document
        ),


        # -------------------------------------------------
        # Whether a document is active
        # -------------------------------------------------

        "document_context": (
            request.document_context
        ),


        # -------------------------------------------------
        # OCR context
        # -------------------------------------------------

        "ocr_text": (
            ocr_text
        ),


        # -------------------------------------------------
        # Conversation history
        # -------------------------------------------------

        "history": (
            request.history
        ),


        # -------------------------------------------------
        # Clean output fields
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
    # SAFE RESPONSE
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
    # RESPONSE
    # =====================================================

    return {

        # -------------------------------------------------
        # FINAL ANSWER
        # -------------------------------------------------

        "answer": result.get(
            "answer",
            "",
        ),


        # -------------------------------------------------
        # ROUTE
        #
        # rag
        # web
        # general
        # greeting
        # -------------------------------------------------

        "route": result.get(
            "route",
            "general",
        ),


        # -------------------------------------------------
        # SOURCES
        # -------------------------------------------------

        "sources": result.get(
            "sources",
            [],
        ),


        # -------------------------------------------------
        # ACTIVE DOCUMENT
        # -------------------------------------------------

        "selected_document": result.get(
            "selected_document",
            selected_document,
        ),
    }