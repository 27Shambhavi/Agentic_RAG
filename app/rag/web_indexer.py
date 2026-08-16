from __future__ import annotations

import hashlib

from app.rag.web_loader import web_loader
from app.rag.web_playwright import playwright_loader
from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


WEB_NAMESPACE = "web"

MIN_STATIC_CONTENT = 500


# =========================================================
# WEB ID
# =========================================================

def create_web_id(
    url: str,
) -> str:

    digest = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()

    return (
        "web_"
        + digest[:24]
    )


# =========================================================
# INDEX WEBPAGE
# =========================================================

def index_webpage(
    url: str,
) -> dict:

    url = (
        url or ""
    ).strip()

    if not url:

        raise ValueError(
            "URL cannot be empty."
        )

    print(
        "\n================ WEB INDEXER ================"
    )

    print(
        "URL:",
        url,
    )

    # =====================================================
    # TRY STATIC HTML FIRST
    # =====================================================

    static_page = None

    try:

        static_page = web_loader.load(
            url
        )

        print(
            "Static loader:",
            static_page.method,
        )

        print(
            "Static characters:",
            len(static_page.text),
        )

    except Exception as error:

        print(
            "[STATIC WEB LOADER ERROR]",
            repr(error),
        )

    # =====================================================
    # PLAYWRIGHT FALLBACK
    # =====================================================

    if (
        static_page is None
        or len(
            static_page.text.strip()
        ) < MIN_STATIC_CONTENT
    ):

        print(
            "Static content insufficient."
        )

        print(
            "Using Playwright..."
        )

        dynamic_page = (
            playwright_loader.load(
                url
            )
        )

        text = dynamic_page[
            "text"
        ]

        title = dynamic_page[
            "title"
        ]

        method = dynamic_page[
            "method"
        ]

    else:

        text = static_page.text

        title = static_page.title

        method = static_page.method

    # =====================================================
    # VALIDATE
    # =====================================================

    if len(
        text.strip()
    ) < 100:

        raise ValueError(
            "Could not extract meaningful "
            "content from this webpage."
        )

    print(
        "Final loader:",
        method,
    )

    print(
        "Final text length:",
        len(text),
    )

    # =====================================================
    # CREATE PAGE
    # =====================================================

    pages = [
        {
            "text": text,
            "page": 1,
            "source": url,
        }
    ]

    # =====================================================
    # CHUNK
    # =====================================================

    chunks = chunk_text(
        pages,
        chunk_size=800,
        chunk_overlap=100,
    )

    if not chunks:

        raise ValueError(
            "No chunks generated."
        )

    print(
        "Chunks:",
        len(chunks),
    )

    # =====================================================
    # EMBEDDINGS
    # =====================================================

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = (
        embedding_model.embed_documents(
            texts
        )
    )

    # =====================================================
    # WEB DOCUMENT ID
    # =====================================================

    web_id = create_web_id(
        url
    )

    # =====================================================
    # VECTORS
    # =====================================================

    vectors = []

    for index, (
        chunk,
        embedding,
    ) in enumerate(
        zip(
            chunks,
            embeddings,
        )
    ):

        vectors.append(
            {
                "id": (
                    f"{web_id}_"
                    f"{index}"
                ),

                "values": embedding,

                "metadata": {
                    "source": url,
                    "source_type": "web",
                    "web_id": web_id,
                    "title": title,
                    "chunk_id": index,
                    "loader": method,
                    "page": 1,
                    "text": chunk["text"],
                },
            }
        )

    # =====================================================
    # PINECONE
    # =====================================================

    pinecone_client.upsert(
        vectors=vectors,
        namespace=WEB_NAMESPACE,
    )

    print(
        "Vectors indexed:",
        len(vectors),
    )

    print(
        "Namespace:",
        WEB_NAMESPACE,
    )

    print(
        "============================================\n"
    )

    return {
        "url": url,
        "title": title,
        "web_id": web_id,
        "loader": method,
        "chunks": len(chunks),
        "vectors": len(vectors),
        "namespace": WEB_NAMESPACE,
    }