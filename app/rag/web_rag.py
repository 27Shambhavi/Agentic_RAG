from __future__ import annotations

import hashlib
import re
import time
from urllib.parse import urlparse

from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client
from app.rag.web_scraper import scrape_url
from app.llm.gemini import llm


# ============================================================
# CONFIG
# ============================================================

WEB_CHUNK_SIZE = 800
WEB_CHUNK_OVERLAP = 100

WEB_TOP_K = 6

WEB_RAG_SCORE_THRESHOLD = 0.20

WEB_CACHE_TTL = 900

WEB_SUMMARY_MAX_CHUNKS = 12


# ============================================================
# PROCESS CACHE
# ============================================================

_WEB_INDEX_CACHE: dict[str, dict] = {}


# ============================================================
# URL HELPERS
# ============================================================

def validate_url(
    url: str,
) -> bool:

    url = (
        url or ""
    ).strip()

    if not url:
        return False

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        return False

    return (
        parsed.scheme in {
            "http",
            "https",
        }
        and bool(
            parsed.netloc
        )
    )


def extract_url(
    text: str,
) -> str:

    text = (
        text or ""
    ).strip()

    if not text:
        return ""

    match = re.search(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    url = (
        match.group(0)
        .strip()
        .rstrip(
            ".,!?;:)]}"
        )
    )

    return (
        normalize_url(url)
        if validate_url(url)
        else ""
    )


def normalize_url(
    url: str,
) -> str:

    url = (
        url or ""
    ).strip()

    if not url:
        return ""

    if not url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        url = (
            "https://"
            + url
        )

    parsed = urlparse(
        url
    )

    scheme = (
        parsed.scheme.lower()
    )

    netloc = (
        parsed.netloc.lower()
    )

    path = (
        parsed.path.rstrip("/")
    )

    result = (
        f"{scheme}://"
        f"{netloc}"
        f"{path}"
    )

    if parsed.query:

        result += (
            f"?{parsed.query}"
        )

    return result


# ============================================================
# DOCUMENT ID
# ============================================================

def create_web_document_id(
    url: str,
) -> str:

    normalized = normalize_url(
        url
    )

    digest = hashlib.sha256(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        f"web_{digest}"
    )


# ============================================================
# SCRAPED PAGE
# ============================================================

def scraped_page_to_dict(
    scraped,
) -> dict:

    if isinstance(
        scraped,
        dict,
    ):

        return scraped

    if hasattr(
        scraped,
        "url",
    ):

        return {
            "url": getattr(
                scraped,
                "url",
                "",
            ),
            "title": getattr(
                scraped,
                "title",
                "",
            ),
            "text": getattr(
                scraped,
                "text",
                "",
            ),
            "method": getattr(
                scraped,
                "method",
                "",
            ),
            "status_code": getattr(
                scraped,
                "status_code",
                200,
            ),
        }

    raise TypeError(
        "Unsupported scraper result."
    )


# ============================================================
# CHUNK
# ============================================================

def chunk_web_content(
    scraped: dict,
) -> list[dict]:

    text = (
        scraped.get(
            "text",
            "",
        )
        or ""
    ).strip()

    if not text:
        return []

    pages = [
        {
            "text": text,
            "page": 1,
            "source": scraped.get(
                "url",
                "",
            ),
            "title": scraped.get(
                "title",
                "",
            ),
        }
    ]

    return (
        chunk_text(
            pages,
            chunk_size=WEB_CHUNK_SIZE,
            chunk_overlap=WEB_CHUNK_OVERLAP,
        )
        or []
    )


# ============================================================
# INDEX WEB PAGE
# ============================================================

def index_web_page(
    url: str,
) -> dict:

    url = normalize_url(
        url
    )

    if not validate_url(url):

        raise ValueError(
            f"Invalid URL: {url}"
        )

    print(
        "\n================ WEB INDEX ================"
    )

    print(
        "URL:",
        url,
    )

    # ========================================================
    # SCRAPE
    # ========================================================

    scraped = scrape_url(
        url
    )

    scraped = scraped_page_to_dict(
        scraped
    )

    text = (
        scraped.get(
            "text",
            "",
        )
        or ""
    ).strip()

    if not text:

        raise ValueError(
            "No meaningful webpage content was extracted."
        )

    title = (
        scraped.get(
            "title",
            "",
        )
        or "Untitled Webpage"
    )

    method = (
        scraped.get(
            "method",
            "",
        )
        or "unknown"
    )

    # ========================================================
    # CHUNK
    # ========================================================

    chunks = chunk_web_content(
        scraped
    )

    if not chunks:

        raise ValueError(
            "No webpage chunks were generated."
        )

    # ========================================================
    # EMBEDDINGS
    # ========================================================

    usable_chunks = []

    for chunk in chunks:

        content = (
            chunk.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if content:

            usable_chunks.append(
                chunk
            )

    texts = [
        chunk["text"]
        for chunk in usable_chunks
    ]

    embeddings = (
        embedding_model.embed_documents(
            texts
        )
    )

    if len(embeddings) != len(texts):

        raise ValueError(
            "Embedding count does not match chunk count."
        )

    # ========================================================
    # DOCUMENT ID
    # ========================================================

    document_id = (
        create_web_document_id(
            url
        )
    )

    # ========================================================
    # VECTORS
    # ========================================================

    vectors = []

    for index, (
        chunk,
        embedding,
    ) in enumerate(
        zip(
            usable_chunks,
            embeddings,
        )
    ):

        content = (
            chunk["text"]
            .strip()
        )

        vectors.append(
            {
                "id": (
                    f"{document_id}_{index}"
                ),

                "values": embedding,

                "metadata": {

                    "type": "web",

                    "source": url,

                    "url": url,

                    "title": title,

                    "document_id": document_id,

                    "method": method,

                    "page": chunk.get(
                        "page",
                        1,
                    ),

                    "chunk_index": index,

                    "text": content,
                },
            }
        )

    # ========================================================
    # PERSIST
    # ========================================================

    pinecone_client.upsert(
        vectors
    )

    print(
        "Persisted web vectors:",
        len(vectors),
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "url": url,

        "title": title,

        "method": method,

        "chunks": len(usable_chunks),

        "vectors": len(vectors),

        "document_id": document_id,

        "status": "indexed",

        "_chunks": [
            {
                "text": chunk["text"],
                "page": chunk.get(
                    "page",
                    1,
                ),
                "source": url,
                "title": title,
            }
            for chunk in usable_chunks
        ],
    }


# ============================================================
# CACHE + INDEX
# ============================================================

def get_or_index_web_page(
    url: str,
) -> dict:

    url = normalize_url(
        url
    )

    now = time.time()

    cached = _WEB_INDEX_CACHE.get(
        url
    )

    if cached:

        age = (
            now
            - cached.get(
                "timestamp",
                0,
            )
        )

        if age < WEB_CACHE_TTL:

            return cached["result"]

    result = index_web_page(
        url
    )

    _WEB_INDEX_CACHE[url] = {
        "timestamp": time.time(),
        "result": result,
    }

    return result


# ============================================================
# PINECONE RESULT NORMALIZER
# ============================================================

def _extract_matches(
    result,
) -> list:

    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "matches",
                [],
            )
            or []
        )

    return (
        getattr(
            result,
            "matches",
            [],
        )
        or []
    )


def _match_to_document(
    match,
) -> dict | None:

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

    try:

        score = float(
            raw_score
        )

    except (
        TypeError,
        ValueError,
    ):

        score = 0.0

    text = str(
        metadata.get(
            "text",
            "",
        )
        or ""
    ).strip()

    if not text:

        return None

    return {

        "text": text,

        "source": (
            metadata.get(
                "source",
                "",
            )
            or ""
        ),

        "url": (
            metadata.get(
                "url",
                "",
            )
            or ""
        ),

        "title": (
            metadata.get(
                "title",
                "",
            )
            or ""
        ),

        "page": metadata.get(
            "page",
            1,
        ),

        "score": score,

        "id": match_id,

        "type": "web",
    }


# ============================================================
# RETRIEVE WEB CHUNKS
# ============================================================

def retrieve_web_page(
    query: str,
    url: str = "",
    top_k: int = WEB_TOP_K,
) -> list[dict]:

    query = (
        query or ""
    ).strip()

    url = normalize_url(
        url
    ) if url else ""

    if not query:
        return []

    query_vector = (
        embedding_model.embed_text(
            query
        )
    )

    # ========================================================
    # FIRST:
    # SPECIFIC URL
    # ========================================================

    if url:

        try:

            result = pinecone_client.query(
                vector=query_vector,
                top_k=top_k,
                filter={
                    "type": {
                        "$eq": "web"
                    },
                    "source": {
                        "$eq": url
                    },
                },
            )

            documents = []

            for match in _extract_matches(
                result
            ):

                document = (
                    _match_to_document(
                        match
                    )
                )

                if document:

                    documents.append(
                        document
                    )

            if documents:

                return documents

        except Exception as error:

            print(
                "[WEB URL RETRIEVAL ERROR]",
                repr(error),
            )

    # ========================================================
    # SECOND:
    # ALL STORED WEB PAGES
    # ========================================================

    try:

        result = pinecone_client.query(
            vector=query_vector,
            top_k=top_k,
            filter={
                "type": {
                    "$eq": "web"
                }
            },
        )

    except Exception as error:

        print(
            "[GLOBAL WEB RETRIEVAL ERROR]",
            repr(error),
        )

        return []

    documents = []

    for match in _extract_matches(
        result
    ):

        document = (
            _match_to_document(
                match
            )
        )

        if document:

            documents.append(
                document
            )

    return documents


# ============================================================
# DIRECT WEB DOCUMENTS
# ============================================================

def build_direct_web_documents(
    index_result: dict,
) -> list[dict]:

    documents = []

    raw_chunks = (
        index_result.get(
            "_chunks",
            [],
        )
        or []
    )

    for index, chunk in enumerate(
        raw_chunks[
            :WEB_SUMMARY_MAX_CHUNKS
        ],
        start=1,
    ):

        if not isinstance(
            chunk,
            dict,
        ):
            continue

        text = (
            chunk.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": (
                    chunk.get(
                        "source",
                        index_result.get(
                            "url",
                            "",
                        ),
                    )
                    or ""
                ),
                "url": index_result.get(
                    "url",
                    "",
                ),
                "title": (
                    chunk.get(
                        "title",
                        index_result.get(
                            "title",
                            "",
                        ),
                    )
                    or ""
                ),
                "page": chunk.get(
                    "page",
                    1,
                ),
                "score": 1.0,
                "id": (
                    f"direct_web_{index}"
                ),
                "type": "web",
            }
        )

    return documents


# ============================================================
# CONTEXT
# ============================================================

def build_web_context(
    documents: list[dict],
) -> str:

    parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        parts.append(
            f"""
SOURCE {index}

TITLE:
{document.get("title", "")}

URL:
{document.get("url", document.get("source", ""))}

PAGE:
{document.get("page", 1)}

CONTENT:
{document.get("text", "")}
"""
        )

    return "\n\n".join(parts)


# ============================================================
# HISTORY
# ============================================================

def build_history(
    history: list[dict],
) -> str:

    parts = []

    for message in history[-8:]:

        if not isinstance(
            message,
            dict,
        ):
            continue

        role = str(
            message.get(
                "role",
                "user",
            )
        ).upper()

        content = str(
            message.get(
                "content",
                "",
            )
            or "",
        ).strip()

        if content:

            parts.append(
                f"{role}: {content}"
            )

    return (
        "\n".join(parts)
        if parts
        else "No previous conversation."
    )


# ============================================================
# WEB RAG
# ============================================================

def web_rag(
    query: str,
    url: str = "",
    history: list[dict] | None = None,
) -> dict:

    query = (
        query or ""
    ).strip()

    history = (
        history
        if isinstance(
            history,
            list,
        )
        else []
    )

    url = (
        normalize_url(url)
        if url
        else ""
    )

    if not query:

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
        }

    # ========================================================
    # URL IN CURRENT QUERY
    # ========================================================

    current_query_url = extract_url(
        query
    )

    if current_query_url:

        url = current_query_url

    # ========================================================
    # IF URL IS PROVIDED, INDEX IT
    # ========================================================

    index_result = {}

    if url:

        try:

            index_result = (
                get_or_index_web_page(
                    url
                )
            )

        except Exception as error:

            print(
                "[WEB INDEX ERROR]",
                repr(error),
            )

            # We do not immediately fail.
            # Persisted vectors may already exist.

    # ========================================================
    # REMOVE URL FROM QUESTION
    # ========================================================

    semantic_query = re.sub(
        r"https?://[^\s<>\"']+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()

    # ========================================================
    # URL ONLY
    # ========================================================

    if not semantic_query:

        if index_result:

            documents = (
                build_direct_web_documents(
                    index_result
                )
            )

        else:

            documents = retrieve_web_page(
                query=(
                    "main purpose "
                    "important information "
                    "services products topics"
                ),
                url=url,
            )

        if not documents:

            return {
                "relevant": False,
                "answer": "",
                "sources": [],
                "documents": [],
                "url": url,
            }

        best_score = 1.0

        instruction = """
The user supplied a webpage URL without a specific question.

Give a useful overview of the webpage.

Explain the main purpose, important topics, services,
products, sections, and facts that are actually present.

Use only the webpage content.
"""

    # ========================================================
    # SPECIFIC QUESTION
    # ========================================================

    else:

        documents = retrieve_web_page(
            query=semantic_query,
            url=url,
            top_k=WEB_TOP_K,
        )

        if not documents:

            return {
                "relevant": False,
                "answer": "",
                "sources": [],
                "documents": [],
                "url": url,
            }

        best_score = max(
            float(
                document.get(
                    "score",
                    0.0,
                )
            )
            for document in documents
        )

        if best_score < WEB_RAG_SCORE_THRESHOLD:

            return {
                "relevant": False,
                "answer": "",
                "sources": documents,
                "documents": documents,
                "best_score": best_score,
                "url": url,
            }

        instruction = f"""
Answer this question:

{semantic_query}

Use only the retrieved webpage content.

If the answer is not present in the retrieved content,
say that it was not found on the webpage.
"""

    # ========================================================
    # GENERATION
    # ========================================================

    context = build_web_context(
        documents
    )

    prompt = f"""
You are the Web RAG answering component.

WEBPAGE:
{url or "Stored web knowledge base"}

CONVERSATION:
{build_history(history)}

RETRIEVED WEB CONTENT:
{context}

{instruction}

RULES:

1. Use only the supplied web content.
2. Do not invent facts.
3. Do not use outside knowledge.
4. Do not mention Pinecone.
5. Do not mention embeddings.
6. Do not mention vector databases.
7. Do not mention retrieval.
8. Do not mention routing.
9. Answer naturally.

ANSWER:
"""

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[WEB RAG LLM ERROR]",
            repr(error),
        )

        return {
            "relevant": False,
            "answer": "",
            "sources": documents,
            "documents": documents,
            "best_score": best_score,
            "generation_error": str(error),
            "url": url,
        }

    answer = (
        answer or ""
    ).strip()

    if not answer:

        return {
            "relevant": False,
            "answer": "",
            "sources": documents,
            "documents": documents,
            "best_score": best_score,
            "url": url,
        }

    # ========================================================
    # SOURCES
    # ========================================================

    sources = []

    for document in documents:

        sources.append(
            {
                "source": document.get(
                    "source",
                    url,
                ),
                "url": document.get(
                    "url",
                    url,
                ),
                "title": document.get(
                    "title",
                    "",
                ),
                "page": document.get(
                    "page",
                    1,
                ),
                "score": round(
                    float(
                        document.get(
                            "score",
                            0.0,
                        )
                    ),
                    4,
                ),
            }
        )

    return {

        "relevant": True,

        "answer": answer,

        "sources": sources,

        "documents": documents,

        "best_score": best_score,

        "url": url,

        "title": index_result.get(
            "title",
            documents[0].get(
                "title",
                "",
            )
            if documents
            else "",
        ),

        "scraping_method": index_result.get(
            "method",
            "",
        ),

        "index": {
            key: value
            for key, value in index_result.items()
            if key != "_chunks"
        },
    }