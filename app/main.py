from fastapi import FastAPI

from app.api.routes import (
    chat_router,
    document_router,
    voice_router,
    multimodal_router,
    health_router,
)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="Agentic RAG Assistant",
    description=(
        "Multimodal Agentic RAG system "
        "with document search, web search, "
        "OCR, vision and voice capabilities."
    ),
    version="1.0.0",
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    health_router
)

app.include_router(
    chat_router
)

app.include_router(
    document_router
)

app.include_router(
    voice_router
)

app.include_router(
    multimodal_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Agentic RAG Assistant API",
        "status": "running",
    }