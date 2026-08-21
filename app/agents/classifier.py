from __future__ import annotations

from app.llm.gemini import llm


# ============================================================
# VALID ROUTES
# ============================================================

VALID_ROUTES = {
    "greeting",
    "rag",
    "web",
    "web_rag",
    "weather",
    "general",
    "ocr",
}


# ============================================================
# CLEAN / VALIDATE ROUTE
# ============================================================

def _clean_route(
    value: str,
) -> str:

    value = (
        str(value or "")
        .strip()
        .lower()
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
    )

    # --------------------------------------------------------
    # Exact route
    # --------------------------------------------------------

    if value in VALID_ROUTES:
        return value

    # --------------------------------------------------------
    # Token route
    # --------------------------------------------------------

    tokens = (
        value
        .replace(":", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace("\n", " ")
        .split()
    )

    for token in tokens:

        if token in VALID_ROUTES:
            return token

    print(
        "[CLASSIFIER INVALID ROUTE]",
        repr(value),
    )

    # Safe fallback.
    return "general"


# ============================================================
# HISTORY
# ============================================================

def _build_history_text(
    history: list[dict],
) -> str:

    items = []

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
        ).strip().upper()

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if content:

            items.append(
                f"{role}: {content}"
            )

    if not items:
        return "No previous conversation."

    return "\n".join(items)


# ============================================================
# CLASSIFY INTENT
# ============================================================

def classify_intent(
    query: str,
    history: list[dict] | None = None,
    ocr_text: str = "",
    selected_document: str = "",
    document_context: bool = False,
    web_url: str = "",
    web_context: bool = False,
) -> str:

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

    ocr_text = (
        ocr_text or ""
    ).strip()

    selected_document = (
        selected_document or ""
    ).strip()

    web_url = (
        web_url or ""
    ).strip()

    # ========================================================
    # EMPTY
    # ========================================================

    if not query:
        return "general"

    # ========================================================
    # CONTEXT FLAGS
    # ========================================================

    document_active = bool(
        selected_document
        or document_context
    )

    webpage_active = bool(
        web_url
        and web_context
    )

    # ========================================================
    # HISTORY
    # ========================================================

    history_text = _build_history_text(
        history
    )

    # ========================================================
    # CONTEXT DESCRIPTION
    # ========================================================

    if webpage_active:

        context = f"""
ACTIVE WEBPAGE CONTEXT

URL:
{web_url}

The webpage was previously supplied by the user and its
content has been indexed.

Use WEB_RAG when the current request is about:

- the webpage
- the page
- the article
- the website
- its contents
- its sections
- its products
- its services
- facts or claims on the page
- anything referred to using conversational references
  such as "it", "this", "that page", "there", or
  "the website"

Use WEB when the current request is unrelated to this
webpage but requires external internet information.

Do NOT force unrelated requests into WEB_RAG.
"""

    elif document_active:

        context = f"""
ACTIVE DOCUMENT KNOWLEDGE CONTEXT

Selected document:

{selected_document or "Document context available"}

IMPORTANT:

The selected document is UI context only.

RAG searches the ENTIRE Pinecone knowledge base.

RAG must NOT be restricted to the selected document.

A normal factual, knowledge, document, policy,
procedure, or information question should go to RAG.

If RAG cannot find sufficiently relevant information,
the graph will automatically fall back to WEB.

If the user explicitly requests current/latest/live
internet information or explicitly asks for web search,
use WEB.

Greetings and ordinary conversation must remain
GREETING or GENERAL.
"""

    else:

        context = """
NO ACTIVE WEBPAGE CONTEXT

The application has a document knowledge-base RAG system.

For a factual, informational, knowledge-base, policy,
document, definition, procedure, or other answerable
knowledge question:

PREFER RAG FIRST.

RAG searches the ENTIRE knowledge base.

If RAG cannot find sufficiently relevant information,
the graph automatically falls back to WEB.

Use WEB directly when the user explicitly asks for
web/internet search or clearly requests current,
latest, live, recent external information.

Use GENERAL for ordinary conversation, creative work,
rewriting, brainstorming, coding help, opinions,
and other tasks that do not require retrieval.

Use GREETING for social/conversational intent.

Use WEATHER for weather requests.

Use OCR only when OCR text is available AND the user
is asking about information contained in that OCR/image.
"""

    # ========================================================
    # CLASSIFIER PROMPT
    # ========================================================

    prompt = f"""
You are the ROUTER of an Agentic RAG assistant.

Your ONLY task is to classify the user's CURRENT INTENT.

Return EXACTLY ONE route name.

Do NOT explain.
Do NOT return JSON.
Do NOT return markdown.
Do NOT return a sentence.

VALID ROUTES:

greeting
rag
web
web_rag
weather
general
ocr


============================================================
CURRENT CONTEXT
============================================================

{context}


============================================================
CONVERSATION HISTORY
============================================================

{history_text}


============================================================
OCR STATUS
============================================================

OCR AVAILABLE:

{bool(ocr_text)}


============================================================
ROUTING RULES
============================================================


1. GREETING
-----------

Choose:

greeting

when the user's intent is social/conversational.

This includes:

- opening a conversation
- greeting the assistant
- casual social check-ins
- acknowledgements
- thanking the assistant
- conversational closing

IMPORTANT:

Do NOT decide greeting using a fixed hardcoded list of
words.

Understand the meaning of the complete message.

A greeting must NEVER be sent to:

- WEB
- RAG
- WEB_RAG


2. WEATHER
-----------

Choose:

weather

when the user is asking about:

- weather
- temperature
- forecast
- rain
- snow
- humidity
- storms
- weather conditions
- climate conditions


3. OCR
-------

Choose:

ocr

ONLY when:

- OCR text is available
AND
- the user is asking about information contained in
  the OCR/image.

The existence of OCR text alone is NOT enough.


4. WEB_RAG
----------

Choose:

web_rag

ONLY when:

- an active webpage exists
AND
- the user's current question is about that webpage.

Use conversation history to understand references such as:

- it
- this
- that
- there
- this page
- that page
- the website
- the article
- the site

Example:

User:
https://example.com

Assistant:
webpage retrieved

User:
what does it say about pricing?

Route:

web_rag


5. RAG
------

Choose:

rag

for normal factual/knowledge/document questions where
the answer may exist in the application's knowledge base.

IMPORTANT:

The selected PDF does NOT restrict retrieval.

The RAG system searches the ENTIRE knowledge base.

Even if there is no selected PDF, RAG can still be used.

The RAG node performs the relevance check.

If RAG cannot answer from the knowledge base,
the graph automatically sends the request to WEB.


6. WEB
------

Choose:

web

when the user genuinely requires external internet
information.

Examples include:

- explicit web search
- explicit internet search
- search online
- google this
- browse the web
- current information
- latest information
- today's information
- recent events
- live information
- current prices
- current status
- external information


7. GENERAL
----------

Choose:

general

for tasks that do not require document or web retrieval.

Examples:

- creative writing
- rewriting
- brainstorming
- opinions
- coding explanations
- programming help
- general explanations
- ordinary conversation
- casual discussion


============================================================
IMPORTANT DECISION LOGIC
============================================================

Understand the user's actual intent.

Do NOT classify based only on individual keywords.

When a question could reasonably be answered from the
knowledge base:

PREFER RAG.

RAG will perform relevance checking.

If RAG fails:

RAG -> WEB

Current/latest/live requests should prefer WEB.

Active webpage questions should use WEB_RAG.

Social/conversational intent should use GREETING.


============================================================
EXAMPLES
============================================================

Example 1:

User:
hello

Route:
greeting


Example 2:

User:
hey, how's everything going?

Route:
greeting


Example 3:

User:
Can you help me understand this concept?

Route:
general


Example 4:

User:
what is the leave policy?

If knowledge base may contain the answer:

Route:
rag


Example 5:

User:
what is the latest leave policy?

Route:
web


Example 6:

User:
who is the current president of India?

Route:
web


Example 7:

User:
write a Python function to reverse a string

Route:
general


Example 8:

User:
what is the weather in Indore?

Route:
weather


Example 9:

User:
what does this page say about refunds?

If an active webpage exists:

Route:
web_rag


Example 10:

User:
what does this image say?

If OCR is available:

Route:
ocr


============================================================
USER QUESTION
============================================================

{query}


============================================================
RETURN ONLY ONE ROUTE
============================================================
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    try:

        result = llm.generate(
            prompt
        )

        print(
            "\n========== CLASSIFIER =========="
        )

        print(
            "Question:",
            query,
        )

        print(
            "Raw route:",
            repr(result),
        )

        route = _clean_route(
            result
        )

        print(
            "Final route:",
            route,
        )

        print(
            "================================\n"
        )

        return route

    except Exception as error:

        print(
            "[CLASSIFIER ERROR]",
            repr(error),
        )

        return "general"