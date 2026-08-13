from app.llm.gemini import llm
from app.rag.retriever import retrieve
from app.rag.citations import format_sources


# =========================================================
# DOCUMENT RAG
# =========================================================

def document_rag(
    query: str,
    selected_document: str = "",
) -> dict:

    query = (query or "").strip()

    selected_document = (
        selected_document or ""
    ).strip()


    # =====================================================
    # VALIDATION
    # =====================================================

    if not query:

        return {
            "answer": "",
            "sources": [],
        }


    # =====================================================
    # ACTIVE DOCUMENT REQUIRED
    # =====================================================

    if not selected_document:

        return {
            "answer": (
                "Please select a document before "
                "asking a document-based question."
            ),
            "sources": [],
        }


    # =====================================================
    # RETRIEVE FROM ACTIVE DOCUMENT ONLY
    # =====================================================

    documents = retrieve(
        query=query,
        top_k=5,
        selected_document=selected_document,
    )


    # =====================================================
    # NO RELEVANT INFORMATION
    # =====================================================

    if not documents:

        return {
            "answer": (
                "I could not find relevant information "
                "in the active document."
            ),
            "sources": [],
        }


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context_parts = []


    for index, doc in enumerate(
        documents,
        start=1,
    ):

        source = doc.get(
            "source",
            selected_document,
        )

        page = doc.get(
            "page",
            "",
        )

        text = doc.get(
            "text",
            "",
        )


        context_parts.append(
            f"""
SOURCE {index}
Document: {source}
Page: {page}

{text}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    # =====================================================
    # RAG PROMPT
    # =====================================================

    prompt = f"""
You are a document question-answering assistant.

The user is asking about the currently active document.

ACTIVE DOCUMENT:
{selected_document}

Answer the user's question using ONLY the
provided document context.

IMPORTANT RULES:

1. Use only the provided document context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer is not present in the context,
   clearly say that it is not available in the document.
5. Answer naturally and concisely.
6. Do not mention embeddings.
7. Do not mention Pinecone.
8. Do not mention retrieval.
9. Do not mention internal implementation.
10. Do not answer from your general knowledge.
11. Stay focused on the active document.

USER QUESTION:

{query}

DOCUMENT CONTEXT:

{context}

ANSWER:
"""


    # =====================================================
    # GENERATE ANSWER
    # =====================================================

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
            "answer": (
                "I couldn't generate an answer "
                "from the active document."
            ),
            "sources": [],
        }


    # =====================================================
    # FORMAT SOURCES
    # =====================================================

    try:

        sources = format_sources(
            documents
        )

    except Exception as error:

        print(
            "[SOURCE FORMAT ERROR]",
            repr(error),
        )

        sources = []


    # =====================================================
    # RETURN
    # =====================================================

    return {
        "answer": answer,
        "sources": sources,
    }