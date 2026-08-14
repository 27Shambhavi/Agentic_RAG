from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


def normalize_filename(name: str) -> str:
    return (
        str(name or "")
        .strip()
        .lower()
    )


def retrieve(
    query: str,
    top_k: int = 5,
    selected_document: str = "",
) -> list[dict]:

    query = (
        query or ""
    ).strip()

    selected_document = (
        selected_document or ""
    ).strip()

    if not query:
        return []

    print(
        "\n================ RETRIEVER ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    # =====================================================
    # EMBEDDING
    # =====================================================

    try:

        query_vector = embedding_model.embed_text(
            query
        )

    except Exception as error:

        print(
            "[RETRIEVER EMBEDDING ERROR]",
            repr(error),
        )

        return []

    print(
        "Query vector dimension:",
        len(query_vector),
    )

    # =====================================================
    # PINECONE QUERY
    #
    # IMPORTANT:
    # Query the index directly because this is the
    # confirmed working Pinecone path.
    # =====================================================

    candidate_k = max(
        top_k * 10,
        50,
    )

    try:

        result = pinecone_client.index.query(
            vector=query_vector,
            top_k=candidate_k,
            namespace="default",
            include_metadata=True,
        )

    except Exception as error:

        print(
            "[PINECONE QUERY ERROR]",
            repr(error),
        )

        return []

    matches = (
        result.get(
            "matches",
            [],
        )
        or []
    )

    print(
        "Pinecone candidates:",
        len(matches),
    )

    # =====================================================
    # NORMALIZE SELECTED DOCUMENT
    # =====================================================

    selected_normalized = normalize_filename(
        selected_document
    )

    print(
        "Normalized selected document:",
        repr(selected_normalized),
    )

    # =====================================================
    # FILTER DOCUMENT
    # =====================================================

    documents = []

    for match in matches:

        metadata = (
            match.get(
                "metadata",
                {},
            )
            or {}
        )

        source = str(
            metadata.get(
                "source",
                "",
            )
        ).strip()

        text = str(
            metadata.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            continue

        source_normalized = normalize_filename(
            source
        )

        # -------------------------------------------------
        # SELECTED DOCUMENT FILTER
        # -------------------------------------------------

        if selected_normalized:

            if source_normalized != selected_normalized:

                continue

        # -------------------------------------------------
        # ADD DOCUMENT
        # -------------------------------------------------

        try:

            score = float(
                match.get(
                    "score",
                    0.0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            score = 0.0

        documents.append(
            {
                "id": match.get(
                    "id",
                    "",
                ),

                "text": text,

                "source": (
                    source
                    or selected_document
                ),

                "page": metadata.get(
                    "page",
                    "",
                ),

                "score": score,
            }
        )

    # =====================================================
    # SORT BY RELEVANCE
    # =====================================================

    documents.sort(
        key=lambda item: item.get(
            "score",
            0.0,
        ),
        reverse=True,
    )

    # =====================================================
    # TOP K
    # =====================================================

    documents = documents[:top_k]

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n------------- RAG MATCHES -------------"
    )

    print(
        "Selected document:",
        selected_document,
    )

    print(
        "Selected document matches:",
        len(documents),
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"[{index}] "
            f"SCORE={document['score']:.4f} "
            f"SOURCE={repr(document['source'])} "
            f"PAGE={document['page']}"
        )

    print(
        "----------------------------------------"
    )

    print(
        "===========================================\n"
    )

    return documents