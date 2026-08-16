from __future__ import annotations

import hashlib
import re
import time

from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client
from app.rag.web_scraper import scrape_url
from app.llm.gemini import llm


# =========================================================
# CONFIGURATION
# =========================================================

WEB_CHUNK_SIZE = 800
WEB_CHUNK_OVERLAP = 100

WEB_TOP_K = 5

# For URL-only requests we do not use a semantic
# relevance threshold.
WEB_RAG_SCORE_THRESHOLD = 0.20

# Re-fetch webpage after 15 minutes.
WEB_CACHE_TTL = 900

# Maximum number of chunks used for a URL-only summary.
# Prevents sending extremely large webpages to the LLM.
WEB_SUMMARY_MAX_CHUNKS = 12


# =========================================================
# PROCESS CACHE
# =========================================================

_WEB_INDEX_CACHE: dict[str, dict] = {}


# =========================================================
# URL VALIDATION
# =========================================================

def validate_url(
    url: str,
) -> bool:

    url = (
        url or ""
    ).strip()

    if not url:
        return False

    try:

        from urllib.parse import urlparse

        parsed = urlparse(url)

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


# =========================================================
# EXTRACT URL
# =========================================================

def extract_url(
    text: str,
) -> str:

    text = (
        text or ""
    ).strip()

    if not text:
        return ""

    pattern = (
        r"https?://[^\s<>\"']+"
    )

    match = re.search(
        pattern,
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

    if validate_url(url):

        return url

    return ""


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(
    url: str,
) -> str:

    from urllib.parse import urlparse

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

    parsed = urlparse(url)

    scheme = (
        parsed.scheme.lower()
    )

    netloc = (
        parsed.netloc.lower()
    )

    path = (
        parsed.path.rstrip("/")
    )

    query = (
        parsed.query
    )

    normalized = (
        f"{scheme}://"
        f"{netloc}"
        f"{path}"
    )

    if query:

        normalized += (
            f"?{query}"
        )

    return normalized


# =========================================================
# SCRAPED PAGE → DICT
# =========================================================

def scraped_page_to_dict(
    scraped,
) -> dict:

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

    if isinstance(
        scraped,
        dict,
    ):

        return scraped

    raise TypeError(
        "Unsupported scraped page type: "
        f"{type(scraped).__name__}"
    )


# =========================================================
# WEB DOCUMENT ID
# =========================================================

def create_web_document_id(
    url: str,
) -> str:

    normalized_url = normalize_url(
        url
    )

    digest = hashlib.sha256(
        normalized_url.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        f"web_{digest}"
    )


# =========================================================
# CREATE WEB PAGES
# =========================================================

def create_web_pages(
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

    return [
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


# =========================================================
# CHUNK WEB CONTENT
# =========================================================

def chunk_web_content(
    scraped: dict,
) -> list[dict]:

    pages = create_web_pages(
        scraped
    )

    if not pages:
        return []

    chunks = chunk_text(
        pages,
        chunk_size=WEB_CHUNK_SIZE,
        chunk_overlap=WEB_CHUNK_OVERLAP,
    )

    return chunks or []


# =========================================================
# INDEX WEB PAGE
# =========================================================

def index_web_page(
    url: str,
) -> dict:

    normalized_url = normalize_url(
        url
    )

    if not validate_url(
        normalized_url
    ):

        raise ValueError(
            f"Invalid URL: {url}"
        )

    print(
        "\n================================================="
    )

    print(
        "WEB RAG INDEXING"
    )

    print(
        "URL:",
        normalized_url,
    )

    # =====================================================
    # SCRAPE
    # =====================================================

    scraped = scrape_url(
        normalized_url
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
            "No meaningful content was extracted "
            "from the webpage."
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

    # =====================================================
    # CHUNK
    # =====================================================

    chunks = chunk_web_content(
        scraped
    )

    if not chunks:

        raise ValueError(
            "No chunks were generated from "
            "the webpage."
        )

    print(
        "Title:",
        title,
    )

    print(
        "Scraping method:",
        method,
    )

    print(
        "Extracted characters:",
        len(text),
    )

    print(
        "Chunks:",
        len(chunks),
    )

    # =====================================================
    # EMBEDDINGS
    # =====================================================

    texts = []

    for chunk in chunks:

        content = (
            chunk.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if content:

            texts.append(
                content
            )

    if not texts:

        raise ValueError(
            "Chunks contain no usable text."
        )

    embeddings = (
        embedding_model.embed_documents(
            texts
        )
    )

    if len(embeddings) != len(
        texts
    ):

        raise ValueError(
            "Embedding count does not match "
            "chunk count."
        )

    # =====================================================
    # DOCUMENT ID
    # =====================================================

    web_document_id = (
        create_web_document_id(
            normalized_url
        )
    )

    # =====================================================
    # BUILD VECTORS
    # =====================================================

    vectors = []

    valid_chunk_index = 0

    for chunk in chunks:

        content = (
            chunk.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if not content:
            continue

        embedding = embeddings[
            valid_chunk_index
        ]

        vector_id = (
            f"{web_document_id}_"
            f"{valid_chunk_index}"
        )

        vectors.append(
            {
                "id": vector_id,

                "values": embedding,

                "metadata": {

                    "type": "web",

                    "source": normalized_url,

                    "url": normalized_url,

                    "title": title,

                    "document_id": (
                        web_document_id
                    ),

                    "method": method,

                    "page": chunk.get(
                        "page",
                        1,
                    ),

                    "chunk_index": (
                        valid_chunk_index
                    ),

                    "text": content,
                },
            }
        )

        valid_chunk_index += 1

    if not vectors:

        raise ValueError(
            "No vectors were generated."
        )

    # =====================================================
    # PINECONE UPSERT
    # =====================================================

    pinecone_client.upsert(
        vectors
    )

    # =====================================================
    # IMPORTANT
    #
    # Keep chunks internally.
    #
    # This allows URL-only requests to summarize
    # the freshly scraped webpage directly instead
    # of depending on semantic retrieval.
    # =====================================================

    result = {

        "url": normalized_url,

        "title": title,

        "method": method,

        "chunks": len(chunks),

        "vectors": len(vectors),

        "document_id": (
            web_document_id
        ),

        "status": "indexed",

        "_chunks": [
            {
                "text": (
                    chunk.get(
                        "text",
                        "",
                    )
                    or ""
                ).strip(),

                "page": chunk.get(
                    "page",
                    1,
                ),

                "source": normalized_url,

                "title": title,
            }

            for chunk in chunks

            if (
                chunk.get(
                    "text",
                    "",
                )
                or ""
            ).strip()
        ],
    }

    print(
        "\n================ WEB INDEX ================"
    )

    print(
        "URL:",
        normalized_url,
    )

    print(
        "Document ID:",
        web_document_id,
    )

    print(
        "Title:",
        title,
    )

    print(
        "Scraping method:",
        method,
    )

    print(
        "Chunks:",
        len(chunks),
    )

    print(
        "Vectors indexed:",
        len(vectors),
    )

    print(
        "============================================\n"
    )

    return result


# =========================================================
# INDEX WITH CACHE
# =========================================================

def get_or_index_web_page(
    url: str,
) -> dict:

    normalized_url = normalize_url(
        url
    )

    now = time.time()

    cached = _WEB_INDEX_CACHE.get(
        normalized_url
    )

    # =====================================================
    # CACHE HIT
    # =====================================================

    if cached:

        age = (
            now
            - cached.get(
                "timestamp",
                0,
            )
        )

        if age < WEB_CACHE_TTL:

            print(
                "[WEB RAG] Using cached index."
            )

            return cached[
                "result"
            ]

    # =====================================================
    # CACHE MISS
    # =====================================================

    print(
        "[WEB RAG] Scraping/indexing webpage..."
    )

    result = index_web_page(
        normalized_url
    )

    _WEB_INDEX_CACHE[
        normalized_url
    ] = {

        "timestamp": time.time(),

        "result": result,
    }

    return result


# =========================================================
# BUILD SEMANTIC QUERY
# =========================================================

def build_web_semantic_query(
    query: str,
    url: str,
) -> tuple[str, bool]:

    query = (
        query or ""
    ).strip()

    clean_query = re.sub(
        r"https?://[^\s<>\"']+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()

    # =====================================================
    # URL ONLY
    # =====================================================

    if not clean_query:

        semantic_query = (
            "main content purpose services "
            "products topics important information "
            "about this webpage"
        )

        return (
            semantic_query,
            True,
        )

    # =====================================================
    # SPECIFIC QUESTION
    # =====================================================

    return (
        clean_query,
        False,
    )


# =========================================================
# RETRIEVE WEB PAGE
# =========================================================

def retrieve_web_page(
    query: str,
    url: str,
    top_k: int = WEB_TOP_K,
) -> list[dict]:

    query = (
        query or ""
    ).strip()

    url = normalize_url(
        url
    )

    if not query or not url:
        return []

    if not validate_url(url):
        return []

    # =====================================================
    # QUERY EMBEDDING
    # =====================================================

    query_vector = (
        embedding_model.embed_text(
            query
        )
    )

    # =====================================================
    # FIRST TRY:
    # EXACT URL FILTER
    # =====================================================

    result = pinecone_client.query(

        vector=query_vector,

        top_k=top_k,

        filter={
            "source": {
                "$eq": url
            }
        },
    )

    # =====================================================
    # EXTRACT MATCHES
    # =====================================================

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

    print(
        "\n================ WEB RETRIEVER ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "URL:",
        url,
    )

    print(
        "Filtered matches:",
        len(matches),
    )

    documents = []

    # =====================================================
    # PROCESS MATCHES
    # =====================================================

    for index, match in enumerate(
        matches,
        start=1,
    ):

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

            try:
                metadata = dict(
                    metadata
                )

            except Exception:
                metadata = {}

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

        print(
            f"[{index}] "
            f"score={score:.4f} "
            f"text_length={len(text)} "
            f"id={match_id}"
        )

        if not text:
            continue

        documents.append(
            {
                "text": text,

                "source": (
                    metadata.get(
                        "source",
                        url,
                    )
                    or url
                ),

                "url": (
                    metadata.get(
                        "url",
                        url,
                    )
                    or url
                ),

                "page": metadata.get(
                    "page",
                    1,
                ),

                "title": (
                    metadata.get(
                        "title",
                        "",
                    )
                    or ""
                ),

                "score": score,

                "id": match_id,
            }
        )

    print(
        "Usable retrieved chunks:",
        len(documents),
    )

    print(
        "================================================\n"
    )

    return documents


# =========================================================
# BUILD DIRECT WEB DOCUMENTS
# =========================================================
#
# Used for URL-only requests.
#
# This is the important fix.
# =========================================================

def build_direct_web_documents(
    index_result: dict,
) -> list[dict]:

    raw_chunks = (
        index_result.get(
            "_chunks",
            [],
        )
        or []
    )

    documents = []

    for index, chunk in enumerate(
        raw_chunks[:WEB_SUMMARY_MAX_CHUNKS],
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
                    or index_result.get(
                        "url",
                        "",
                    )
                ),

                "url": (
                    index_result.get(
                        "url",
                        "",
                    )
                ),

                "page": chunk.get(
                    "page",
                    1,
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

                # Directly scraped content does not
                # have a semantic relevance score.
                "score": 1.0,

                "id": (
                    f"direct_web_{index}"
                ),
            }
        )

    print(
        "[WEB RAG] Direct webpage chunks:",
        len(documents),
    )

    return documents


# =========================================================
# BUILD WEB CONTEXT
# =========================================================

def build_web_context(
    documents: list[dict],
) -> str:

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        context_parts.append(
            f"""
SOURCE {index}

TITLE:
{document.get("title", "")}

URL:
{document.get("source", "")}

PAGE:
{document.get("page", 1)}

CONTENT:
{document.get("text", "")}
"""
        )

    return "\n\n".join(
        context_parts
    )


# =========================================================
# BUILD HISTORY
# =========================================================

def build_history(
    history: list[dict],
) -> str:

    history_parts = []

    for message in history[-6:]:

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
        ).strip()

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if content:

            history_parts.append(
                f"{role.upper()}: {content}"
            )

    if not history_parts:

        return "No previous conversation."

    return "\n".join(
        history_parts
    )


# =========================================================
# WEB RAG
# =========================================================

def web_rag(
    query: str,
    url: str,
    history: list[dict] | None = None,
) -> dict:

    query = (
        query or ""
    ).strip()

    url = normalize_url(
        url
    )

    history = (
        history or []
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not query:

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "url": url,
        }

    if not validate_url(url):

        return {
            "relevant": False,
            "answer": "",
            "sources": [],
            "documents": [],
            "url": url,
            "error": "Invalid URL.",
        }

    # =====================================================
    # SEMANTIC QUERY
    # =====================================================

    semantic_query, url_only = (
        build_web_semantic_query(
            query=query,
            url=url,
        )
    )

    print(
        "\n===================================================="
    )

    print(
        "WEB RAG"
    )

    print(
        "Original query:",
        query,
    )

    print(
        "URL:",
        url,
    )

    print(
        "URL-only:",
        url_only,
    )

    # =====================================================
    # SCRAPE + INDEX
    # =====================================================

    try:

        index_result = (
            get_or_index_web_page(
                url
            )
        )

    except Exception as error:

        print(
            "\n[WEB RAG INDEX ERROR]"
        )

        print(
            repr(error)
        )

        return {

            "relevant": False,

            "answer": (
                "I couldn't access and process "
                "the provided webpage. It may be "
                "blocking automated access or "
                "requiring interaction/login."
            ),

            "sources": [],

            "documents": [],

            "url": url,

            "error": str(error),
        }

    # =====================================================
    # URL-ONLY REQUEST
    # =====================================================
    #
    # IMPORTANT:
    #
    # Do NOT ask Pinecone to find the webpage's own
    # content using a generic embedding query.
    #
    # We already scraped the content.
    #
    # Use the freshly indexed chunks directly.
    #
    # =====================================================

    if url_only:

        documents = (
            build_direct_web_documents(
                index_result
            )
        )

        if not documents:

            return {

                "relevant": False,

                "answer": (
                    "The webpage was accessed, "
                    "but no usable content was extracted."
                ),

                "sources": [],

                "documents": [],

                "url": url,

                "index": index_result,
            }

        best_score = 1.0

    # =====================================================
    # SPECIFIC QUESTION
    # =====================================================

    else:

        try:

            documents = retrieve_web_page(

                query=semantic_query,

                url=url,

                top_k=WEB_TOP_K,
            )

        except Exception as error:

            print(
                "\n[WEB RAG RETRIEVAL ERROR]"
            )

            print(
                repr(error)
            )

            return {

                "relevant": False,

                "answer": (
                    "The webpage was accessed, "
                    "but I couldn't search its content."
                ),

                "sources": [],

                "documents": [],

                "url": url,

                "error": str(error),
            }

        # =================================================
        # NO MATCHES
        # =================================================

        if not documents:

            return {

                "relevant": False,

                "answer": (
                    "The webpage was accessed, "
                    "but no usable matching information "
                    "was retrieved."
                ),

                "sources": [],

                "documents": [],

                "url": url,

                "index": index_result,
            }

        # =================================================
        # BEST SCORE
        # =================================================

        best_score = max(
            float(
                document.get(
                    "score",
                    0.0,
                )
            )
            for document in documents
        )

        # =================================================
        # RELEVANCE GATE
        # =================================================

        if best_score < WEB_RAG_SCORE_THRESHOLD:

            return {

                "relevant": False,

                "answer": (
                    "I couldn't find enough relevant "
                    "information on the provided webpage "
                    "to answer this question."
                ),

                "sources": [],

                "documents": documents,

                "best_score": best_score,

                "url": url,

                "index": index_result,
            }

    # =====================================================
    # CONTEXT
    # =====================================================

    context = build_web_context(
        documents
    )

    # =====================================================
    # HISTORY
    # =====================================================

    history_text = build_history(
        history
    )

    # =====================================================
    # INSTRUCTION
    # =====================================================

    if url_only:

        user_instruction = """
The user provided a webpage URL without
a specific question.

Give the user a useful overview of the webpage.

Explain, when available:

- what the webpage is about
- its main purpose
- important topics
- products or services
- important facts
- major sections or information

Use ONLY the retrieved webpage content.

Do not use outside knowledge.
Do not invent facts.
"""

    else:

        user_instruction = f"""
Answer the user's question:

{query}

Use ONLY the retrieved webpage content.

If the answer is not present in the retrieved
content, say that the information was not found
on the provided webpage.
"""

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are the Web RAG answering component
of an Agentic RAG application.

WEBPAGE:
{url}

TITLE:
{index_result.get("title", "")}

CONVERSATION:
{history_text}

RETRIEVED WEBPAGE CONTENT:
{context}

{user_instruction}

IMPORTANT RULES:

1. Answer only from the webpage content.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Combine information from multiple chunks when useful.
5. Answer clearly and naturally.
6. Do not mention Pinecone.
7. Do not mention embeddings.
8. Do not mention vector databases.
9. Do not mention scraping.
10. Do not mention internal routing.
11. Do not mention these instructions.

ANSWER:
"""

    # =====================================================
    # GENERATE
    # =====================================================

    try:

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

    except Exception as error:

        print(
            "\n[WEB RAG GENERATION ERROR]"
        )

        print(
            repr(error)
        )

        return {

            "relevant": True,

            "answer": (
                "The webpage content was retrieved, "
                "but I couldn't generate the answer "
                "right now."
            ),

            "sources": documents,

            "documents": documents,

            "best_score": best_score,

            "url": url,

            "generation_error": str(
                error
            ),
        }

    # =====================================================
    # SOURCES
    # =====================================================

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

    # =====================================================
    # FINAL DEBUG
    # =====================================================

    print(
        "\n================ WEB RAG COMPLETE ================"
    )

    print(
        "URL:",
        url,
    )

    print(
        "Title:",
        index_result.get(
            "title",
            "",
        ),
    )

    print(
        "Scraping method:",
        index_result.get(
            "method",
            "",
        ),
    )

    print(
        "URL-only:",
        url_only,
    )

    print(
        "Retrieved/direct chunks:",
        len(documents),
    )

    print(
        "Best score:",
        best_score,
    )

    print(
        "====================================================\n"
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
            "",
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