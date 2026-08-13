from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


# =========================================================
# RETRIEVE DOCUMENTS
# =========================================================

def retrieve(
    query: str,
    top_k: int = 5,
    selected_document: str = "",
) -> list[dict]:

    query = (query or "").strip()
    selected_document = (
        selected_document or ""
    ).strip()


    # =====================================================
    # VALIDATION
    # =====================================================

    if not query:
        return []


    # =====================================================
    # EMBEDDING
    # =====================================================

    query_vector = embedding_model.embed_text(
        query
    )


    # =====================================================
    # PINECONE FILTER
    # =====================================================
    #
    # If a document is active, ONLY retrieve chunks
    # belonging to that document.
    #
    # metadata:
    #
    # {
    #     "text": "...",
    #     "source": "Ayushman Bharat Yojna.pdf",
    #     "page": 4
    # }
    #
    # =====================================================

    query_kwargs = {
        "vector": query_vector,
        "top_k": top_k,
    }


    if selected_document:

        query_kwargs["filter"] = {
            "source": {
                "$eq": selected_document
            }
        }


    # =====================================================
    # PINECONE SEARCH
    # =====================================================

    result = pinecone_client.query(
        **query_kwargs
    )


    matches = (
        result.get(
            "matches",
            []
        )
        if isinstance(result, dict)
        else []
    )


    # =====================================================
    # BUILD DOCUMENT RESULTS
    # =====================================================

    documents = []


    for match in matches:

        metadata = match.get(
            "metadata",
            {}
        ) or {}


        text = str(
            metadata.get(
                "text",
                ""
            )
        ).strip()


        source = str(
            metadata.get(
                "source",
                ""
            )
        ).strip()


        page = metadata.get(
            "page",
            ""
        )


        score = match.get(
            "score",
            0
        )


        # -------------------------------------------------
        # Ignore empty chunks
        # -------------------------------------------------

        if not text:
            continue


        # -------------------------------------------------
        # Extra safety
        #
        # Even though Pinecone filter is applied,
        # verify source again.
        # -------------------------------------------------

        if selected_document:

            if source != selected_document:
                continue


        documents.append(
            {
                "text": text,
                "source": source,
                "page": page,
                "score": score,
            }
        )


    return documents