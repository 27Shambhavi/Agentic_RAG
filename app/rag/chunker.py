def chunk_text(
    pages: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 100
) -> list[dict]:

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    chunks = []

    for page in pages:

        text = page["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:

                chunks.append(
                    {
                        "text": chunk,
                        "page": page["page"],
                        "source": page["source"],
                    }
                )

            start += chunk_size - chunk_overlap

    return chunks