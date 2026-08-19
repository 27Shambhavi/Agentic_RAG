from __future__ import annotations

from app.rag.citations import format_sources
from app.llm.gemini import llm


NOT_FOUND_MARKER = "__DOCUMENT_NOT_FOUND__"


def document_rag(
    query: str,
    selected_document: str = "",
    history: list[dict] | None = None,
    documents: list[dict] | None = None,
) -> dict:

    query = (
        query or ""
    ).strip()

    selected_document = (
        selected_document or ""
    ).strip()

    history = (
        history
        if isinstance(
            history,
            list,
        )
        else []
    )

    documents = (
        documents
        if isinstance(
            documents,
            list,
        )
        else []
    )

    if not query:
        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "best_score": 0.0,
        }

    if not documents:

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "best_score": 0.0,
        }

    # =====================================================
    # SCORE
    # =====================================================

    scores = []

    for document in documents:

        if not isinstance(
            document,
            dict,
        ):
            continue

        try:

            scores.append(
                float(
                    document.get(
                        "score",
                        0.0,
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    best_score = (
        max(scores)
        if scores
        else 0.0
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        if not isinstance(
            document,
            dict,
        ):
            continue

        text = str(
            document.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if not text:
            continue

        source = str(
            document.get(
                "source",
                "",
            )
            or ""
        )

        page = str(
            document.get(
                "page",
                "",
            )
            or ""
        )

        context_parts.append(
            f"""
SOURCE {index}

SOURCE FILE:
{source}

PAGE:
{page}

CONTENT:
{text}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    if not context.strip():

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
        }

    # =====================================================
    # HISTORY
    # =====================================================

    history_parts = []

    for message in history[-6:]:

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
        ).upper()

        content = str(
            message.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if content:

            history_parts.append(
                f"{role}: {content}"
            )

    history_text = (
        "\n".join(history_parts)
        if history_parts
        else "No previous conversation."
    )

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are the document-answering component of an Agentic RAG
assistant.

The user may have selected a PDF in the interface.

IMPORTANT:
The selected PDF is only UI context.

The retrieved context below may contain information from
ANY indexed document in the knowledge base.

Therefore answer using the retrieved knowledge-base context,
regardless of which PDF is currently selected.

Do NOT restrict the answer to the selected PDF.

ACTIVE SELECTED DOCUMENT:
{selected_document or "NONE"}

CONVERSATION:
{history_text}

RETRIEVED KNOWLEDGE BASE:
{context}

USER QUESTION:
{query}

RULES:

1. Answer only from the retrieved knowledge-base content.

2. Do not use outside knowledge.

3. Do not invent facts.

4. If multiple documents contain useful information,
   combine them.

5. If the requested information is not actually present,
   output exactly:

{NOT_FOUND_MARKER}

6. Do not mention:
   - Pinecone
   - embeddings
   - vector database
   - retrieval
   - routing
   - chunks
   - system prompt

7. Answer naturally.

FINAL ANSWER:
"""

    # =====================================================
    # GENERATE
    # =====================================================

    try:

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

    except Exception as error:

        print(
            "[DOCUMENT RAG LLM ERROR]",
            repr(error),
        )

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
            "generation_error": str(error),
        }

    # =====================================================
    # NOT FOUND
    # =====================================================

    if (
        NOT_FOUND_MARKER
        in answer
    ):

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
        }

    # =====================================================
    # EMPTY
    # =====================================================

    if not answer:

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
        }

    # =====================================================
    # SUCCESS
    # =====================================================

    return {
        "relevant": True,

        "answer": answer,

        "sources": format_sources(
            documents
        ),

        "documents": documents,

        "best_score": best_score,
    }