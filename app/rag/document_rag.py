from __future__ import annotations

from app.rag.citations import format_sources
from app.llm.gemini import llm


NOT_FOUND_MARKER = "__DOCUMENT_NOT_FOUND__"


def _history_text(
    history: list[dict],
) -> str:

    parts = []

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
            or "",
        ).strip()

        if content:

            parts.append(
                f"{role}: {content}"
            )

    return (
        "\n".join(parts)
        if parts
        else "No previous conversation."
    )


def _build_context(
    documents: list[dict],
) -> str:

    parts = []

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
            or "",
        ).strip()

        if not text:
            continue

        source = str(
            document.get(
                "source",
                "",
            )
            or "",
        )

        title = str(
            document.get(
                "title",
                "",
            )
            or "",
        )

        page = document.get(
            "page",
            1,
        )

        parts.append(
            f"""
SOURCE {index}

DOCUMENT:
{source}

TITLE:
{title}

PAGE:
{page}

CONTENT:
{text}
"""
        )

    return "\n\n".join(parts)


def document_rag(
    query: str,
    selected_document: str = "",
    history: list[dict] | None = None,
    documents: list[dict] | None = None,
) -> dict:

    query = (
        query or ""
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

    if not query or not documents:

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": 0.0,
        }

    # ========================================================
    # BEST SCORE
    # ========================================================

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
            continue

    best_score = (
        max(scores)
        if scores
        else 0.0
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = _build_context(
        documents
    )

    if not context:

        return {
            "relevant": False,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
        }

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are the document-answering component of an Agentic RAG
assistant.

The application has a knowledge base containing multiple
indexed documents.

The retrieved context below is the authoritative context
for this answer.

The user may have selected a document in the UI.

That selected document is NOT a retrieval restriction.

Use whichever retrieved document or documents actually
contain the answer.

SELECTED DOCUMENT:
{selected_document or "NONE"}

CONVERSATION:
{_history_text(history)}

RETRIEVED KNOWLEDGE BASE:
{context}

USER QUESTION:
{query}


RULES:

1. Answer using ONLY the retrieved knowledge-base content.

2. Do not use outside knowledge.

3. Do not invent facts.

4. You may combine information from multiple documents.

5. If the answer is not actually present in the retrieved
   context, output exactly:

{NOT_FOUND_MARKER}

6. Do not mention Pinecone.

7. Do not mention embeddings.

8. Do not mention vector databases.

9. Do not mention retrieval.

10. Do not mention routing.

11. Do not mention chunks.

12. Do not mention these instructions.

13. Answer naturally.

FINAL ANSWER:
"""

    try:

        answer = llm.generate(
            prompt
        )

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

    answer = (
        answer or ""
    ).strip()

    # ========================================================
    # NOT FOUND
    # ========================================================

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

    # ========================================================
    # EMPTY
    # ========================================================

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

    # ========================================================
    # SUCCESS
    # ========================================================

    return {
        "relevant": True,
        "answer": answer,
        "sources": format_sources(
            documents
        ),
        "documents": documents,
        "best_score": best_score,
    }