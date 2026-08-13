def format_sources(
    documents: list[dict]
) -> list[dict]:

    sources = []

    for doc in documents:

        sources.append(
            {
                "source": doc["source"],
                "page": doc["page"],
                "score": round(
                    float(doc["score"]),
                    4
                )
            }
        )

    return sources