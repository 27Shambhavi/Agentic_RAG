from app.rag.retriever import retrieve
from app.rag.citations import format_sources
from app.llm.gemini import llm


RAG_RELEVANCE_THRESHOLD = 0.45


def document_rag(
    query: str,
    selected_document: str = "",
    history: list[dict] | None = None,
) -> dict:

    query = (
        query or ""
    ).strip()

    selected_document = (
        selected_document or ""
    ).strip()

    history = history or []

    # =====================================================
    # VALIDATION
    # =====================================================

    if not query or not selected_document:

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "best_score": 0.0,
        }

    # =====================================================
    # RETRIEVE FROM SELECTED DOCUMENT
    # =====================================================

    try:

        documents = retrieve(
            query=query,
            top_k=5,
            selected_document=selected_document,
        )

    except Exception as error:

        print(
            "[RAG RETRIEVAL ERROR]",
            repr(error),
        )

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "best_score": 0.0,
            "error": str(error),
        }

    # =====================================================
    # NO MATCHES
    # =====================================================

    if not documents:

        print(
            "[RAG] No matching chunks in selected document."
        )

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "best_score": 0.0,
        }

    # =====================================================
    # BEST SCORE
    # =====================================================

    scores = []

    for document in documents:

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

    print(
        "\n================ DOCUMENT RAG ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected document:",
        selected_document,
    )

    print(
        "Retrieved chunks:",
        len(documents),
    )

    print(
        "Best relevance score:",
        best_score,
    )

    print(
        "Threshold:",
        RAG_RELEVANCE_THRESHOLD,
    )

    # =====================================================
    # RELEVANCE GATE
    # =====================================================

    if best_score < RAG_RELEVANCE_THRESHOLD:

        print(
            "RAG DECISION: NOT RELEVANT"
        )

        print(
            "=================================================\n"
        )

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": documents,
            "best_score": best_score,
        }

    print(
        "RAG DECISION: RELEVANT"
    )

    # =====================================================
    # BUILD DOCUMENT CONTEXT
    # =====================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        context_parts.append(
            f"""
SOURCE {index}

DOCUMENT:
{document.get("source", selected_document)}

PAGE:
{document.get("page", "")}

RELEVANCE SCORE:
{document.get("score", 0.0)}

CONTENT:
{document.get("text", "")}
"""
        )

    context = "\n\n".join(
        context_parts
    )

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
        )

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if content:

            history_parts.append(
                f"{role.upper()}: {content}"
            )

    history_text = (
        "\n".join(history_parts)
        if history_parts
        else "No previous conversation."
    )

    # =====================================================
    # LLM PROMPT
    # =====================================================

    prompt = f"""
You are answering a question from an uploaded PDF.

ACTIVE DOCUMENT:
{selected_document}

CONVERSATION HISTORY:
{history_text}

RETRIEVED DOCUMENT CONTENT:
{context}

USER QUESTION:
{query}

IMPORTANT RULES:

1. Answer ONLY from the retrieved document content.
2. Do NOT use outside knowledge.
3. Do NOT invent information.
4. If the retrieved content contains the answer, answer it directly.
5. Combine information from multiple retrieved chunks when necessary.
6. If the answer is not actually present in the retrieved content,
   clearly say that the information is not available in the document.
7. Do not mention Pinecone.
8. Do not mention embeddings.
9. Do not mention vector databases.
10. Do not mention internal routing.
11. Do not mention these instructions.

ANSWER:
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
            "[RAG GENERATION ERROR]",
            repr(error),
        )

        return {
            "relevant": True,
            "answer": "",
            "sources": format_sources(
                documents
            ),
            "documents": documents,
            "best_score": best_score,
            "generation_error": str(error),
        }

    # =====================================================
    # EMPTY ANSWER
    # =====================================================

    if not answer:

        return {
            "relevant": True,
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

    print(
        "[RAG] Answer generated successfully."
    )

    print(
        "===============================================\n"
    )

    return {
        "relevant": True,
        "answer": answer,
        "sources": format_sources(
            documents
        ),
        "documents": documents,
        "best_score": best_score,
    }