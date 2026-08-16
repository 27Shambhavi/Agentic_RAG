from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


WEB_NAMESPACE = "web"


def retrieve_web(
    query: str,
    top_k: int = 5,
    url: str = "",
) -> list[dict]:

    query = (
        query or ""
    ).strip()

    url = (
        url or ""
    ).strip()

    if not query:

        return []

    print(
        "\n================ WEB RETRIEVER ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "URL:",
        url or "ALL WEB DOCUMENTS",
    )

    # =====================================================
    # QUERY EMBEDDING
    # =====================================================

    query_vector = (
        embedding_model.embed_text(
            query
        )
    )

    # =====================================================
    # URL FILTER
    # =====================================================

    metadata_filter = None

    if url:

        metadata_filter = {
            "source": {
                "$eq": url
            }
        }

    # =====================================================
    # PINECONE
    # =====================================================

    result = pinecone_client.query(
        vector=query_vector,
        top_k=top_k,
        namespace=WEB_NAMESPACE,
        filter=metadata_filter,
    )

    matches = result.get(
        "matches",
        [],
    )

    documents = []

    for match in matches:

        metadata = (
            match.get(
                "metadata",
                {},
            )
            or {}
        )

        text = str(
            metadata.get(
                "text",
                "",
            )
        ).strip()

        if not text:

            continue

        documents.append(
            {
                "text": text,

                "source": metadata.get(
                    "source",
                    url,
                ),

                "title": metadata.get(
                    "title",
                    "",
                ),

                "score": float(
                    match.get(
                        "score",
                        0.0,
                    )
                ),

                "chunk_id": metadata.get(
                    "chunk_id",
                    "",
                ),

                "loader": metadata.get(
                    "loader",
                    "",
                ),

                "id": match.get(
                    "id",
                    "",
                ),
            }
        )

    print(
        "Retrieved web chunks:",
        len(documents),
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"[{index}] "
            f"SCORE={document['score']:.4f} "
            f"SOURCE={document['source']}"
        )

    print(
        "==============================================\n"
    )

    return documents