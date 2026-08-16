from __future__ import annotations

import re


# =========================================================
# CONFIGURATION
# =========================================================

WEB_CHUNK_SIZE = 800
WEB_CHUNK_OVERLAP = 120


# =========================================================
# CLEAN WEB TEXT
# =========================================================

def normalize_web_text(
    text: str,
) -> str:

    text = (
        text or ""
    ).strip()

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# CHUNK WEB CONTENT
# =========================================================

def chunk_web_text(
    text: str,
    chunk_size: int = WEB_CHUNK_SIZE,
    overlap: int = WEB_CHUNK_OVERLAP,
) -> list[str]:

    text = normalize_web_text(
        text
    )

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    # -----------------------------------------------------
    # Split into words.
    # -----------------------------------------------------

    words = text.split()

    chunks = []

    start = 0

    # -----------------------------------------------------
    # Sliding-window chunking.
    # -----------------------------------------------------

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:

            chunks.append(
                chunk
            )

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# =========================================================
# CHUNK WITH METADATA
# =========================================================

def create_web_chunks(
    text: str,
    url: str,
    title: str,
) -> list[dict]:

    chunks = chunk_web_text(
        text
    )

    results = []

    for index, chunk in enumerate(
        chunks
    ):

        results.append(
            {
                "text": chunk,

                "chunk_index": index,

                "source_type": "web",

                "url": url,

                "title": title,
            }
        )

    return results