from pathlib import Path

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

    query = query.strip()

    selected_document = (
        selected_document.strip()
    )

    # =====================================================
    # RETRIEVE DOCUMENTS
    # =====================================================

    documents = retrieve(
        query=query,
        top_k=20,
    )

    # =====================================================
    # FILTER BY SELECTED DOCUMENT
    # =====================================================

    if selected_document:

        selected_name = Path(
            selected_document
        ).name.lower()

        filtered_documents = []

        for doc in documents:

            source = str(
                doc.get(
                    "source",
                    ""
                )
            )

            source_name = Path(
                source
            ).name.lower()

            if (
                source_name == selected_name
                or selected_name in source_name
                or source_name in selected_name
            ):

                filtered_documents.append(
                    doc
                )

        documents = filtered_documents

    # =====================================================
    # NO RELEVANT DOCUMENTS
    # =====================================================

    if not documents:

        if selected_document:

            message = (
                "I couldn't find relevant information "
                f"in the selected document "
                f"'{selected_document}'."
            )

        else:

            message = (
                "I could not find relevant information "
                "in the uploaded documents."
            )

        return {
            "answer": message,
            "sources": [],
            "context": "",
        }

    # =====================================================
    # BUILD DOCUMENT CONTEXT
    # =====================================================

    context_parts = []

    for index, doc in enumerate(
        documents,
        start=1,
    ):

        source = doc.get(
            "source",
            "Unknown document",
        )

        page = doc.get(
            "page",
            "Unknown",
        )

        text = doc.get(
            "text",
            "",
        )

        context_parts.append(
            f"""
DOCUMENT SOURCE {index}

Source:
{source}

Page:
{page}

Content:
{text}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # =====================================================
    # PROMPT
    # =====================================================

    if selected_document:

        document_instruction = f"""
The user has selected this document:

{selected_document}

Answer ONLY from this selected document.
"""

    else:

        document_instruction = """
Answer using the provided uploaded-document context.
"""

    prompt = f"""
You are a document question-answering assistant.

{document_instruction}

USER QUESTION:
{query}

DOCUMENT CONTEXT:
{context}

RULES:

1. Use ONLY the provided document context.
2. Do NOT use outside knowledge.
3. Do NOT invent facts.
4. If the answer is not present in the context,
   clearly say that the information is not available
   in the selected document.
5. Answer the user's exact question.
6. If the user asks for a summary, summarize the
   retrieved document content.
7. If the user asks a follow-up question, use the
   same document context.
8. Be clear and concise.
9. Do not mention embeddings, retrieval, Pinecone,
   chunks, vector databases, or internal processing.

ANSWER:
"""

    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    answer = llm.generate(
        prompt
    )

    # =====================================================
    # SOURCES
    # =====================================================

    sources = format_sources(
        documents
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "answer": answer,

        "sources": sources,

        "context": context,
    }