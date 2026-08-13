from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

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

    # User question
    message: str

    # Currently selected document
    selected_document: str = ""

    # Whether a document is currently active
    document_context: bool = False


# =========================================================
# CHAT
# =========================================================

@router.post("")
async def chat(
    request: ChatRequest,
):

    query = request.message.strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )


    try:

        # -------------------------------------------------
        # BUILD AGENT STATE
        # -------------------------------------------------

        state = {
            "query": query,

            "selected_document": (
                request.selected_document.strip()
            ),

            "document_context": (
                request.document_context
            ),
        }


        # -------------------------------------------------
        # RUN LANGGRAPH
        # -------------------------------------------------

        result = agent.invoke(
            state
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "answer": result.get(
                "answer",
                "",
            ),

            "route": result.get(
                "route",
                "general",
            ),

            "sources": result.get(
                "sources",
                [],
            ),

            "selected_document": result.get(
                "selected_document",
                request.selected_document,
            ),

        }


    except Exception as error:

        print(
            "\nCHAT ERROR:"
        )

        print(
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )