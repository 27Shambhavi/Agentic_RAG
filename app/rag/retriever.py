from __future__ import annotations

from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


DOCUMENT_NAMESPACE = "default"


def retrieve(
    query: str,
    top_k: int = 8,
) -> list[dict]:

    query = (
        query or ""
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
        "Scope: ENTIRE KNOWLEDGE BASE"
    )

    # ========================================================
    # EMBEDDING
    # ========================================================

    try:

        query_vector = (
            embedding_model.embed_text(
                query
            )
        )

    except Exception as error:

        print(
            "[RETRIEVER EMBEDDING ERROR]",
            repr(error),
        )

        return []

    # ========================================================
    # RETRIEVE MANY CANDIDATES
    # ========================================================

    candidate_k = max(
        top_k * 10,
        50,
    )

    try:

        result = pinecone_client.query(
            vector=query_vector,
            top_k=candidate_k,
            namespace=DOCUMENT_NAMESPACE,
        )

    except Exception as error:

        print(
            "[PINECONE QUERY ERROR]",
            repr(error),
        )

        return []

    if isinstance(
        result,
        dict,
    ):

        matches = (
            result.get(
                "matches",
                [],
            )
            or []
        )

    else:

        matches = (
            getattr(
                result,
                "matches",
                [],
            )
            or []
        )

    documents = []

    for match in matches:

        if isinstance(
            match,
            dict,
        ):

            metadata = (
                match.get(
                    "metadata",
                    {},
                )
                or {}
            )

            match_id = (
                match.get(
                    "id",
                    "",
                )
                or ""
            )

            raw_score = (
                match.get(
                    "score",
                    0.0,
                )
            )

        else:

            metadata = (
                getattr(
                    match,
                    "metadata",
                    {},
                )
                or {}
            )

            match_id = (
                getattr(
                    match,
                    "id",
                    "",
                )
                or ""
            )

            raw_score = (
                getattr(
                    match,
                    "score",
                    0.0,
                )
            )

        if not isinstance(
            metadata,
            dict,
        ):
            continue

        # ----------------------------------------------------
        # Never use WEB vectors for normal PDF RAG.
        # ----------------------------------------------------

        content_type = str(
            metadata.get(
                "type",
                "",
            )
            or ""
        ).strip().lower()

        if content_type == "web":
            continue

        text = str(
            metadata.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if not text:
            continue

        try:

            score = float(
                raw_score
            )

        except (
            TypeError,
            ValueError,
        ):

            score = 0.0

        documents.append(
            {
                "id": match_id,
                "text": text,
                "source": str(
                    metadata.get(
                        "source",
                        "",
                    )
                    or ""
                ),
                "page": metadata.get(
                    "page",
                    "",
                ),
                "title": str(
                    metadata.get(
                        "title",
                        "",
                    )
                    or ""
                ),
                "document_id": str(
                    metadata.get(
                        "document_id",
                        "",
                    )
                    or ""
                ),
                "score": score,
            }
        )

    documents.sort(
        key=lambda item: item.get(
            "score",
            0.0,
        ),
        reverse=True,
    )

    documents = documents[
        :top_k
    ]

    print(
        "Knowledge-base matches:",
        len(documents),
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"[{index}] "
            f"SCORE={document['score']:.4f} "
            f"SOURCE={document['source']} "
            f"PAGE={document['page']}"
        )

    print(
        "============================================\n"
    )

    return documents