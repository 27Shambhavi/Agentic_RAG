# =========================================================
# TEXT CHUNKER
# =========================================================

def chunk_text(
    pages: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[dict]:

    if chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if chunk_overlap < 0:

        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:

        raise ValueError(
            "chunk_overlap must be smaller "
            "than chunk_size."
        )

    chunks = []

    step = (
        chunk_size - chunk_overlap
    )

    for page in pages:

        text = (
            page.get(
                "text",
                "",
            )
            .strip()
        )

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = (
                text[start:end]
                .strip()
            )

            if chunk:

                chunks.append(
                    {
                        "text": chunk,

                        "source": page.get(
                            "source",
                            "",
                        ),

                        "page": page.get(
                            "page",
                            "",
                        ),
                    }
                )

            start += step

    return chunks