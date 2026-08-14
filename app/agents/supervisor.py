from app.agents.state import AgentState
from app.agents.classifier import classify_intent


# =========================================================
# SUPERVISOR
# =========================================================
#
# IMPORTANT ROUTING POLICY
#
# 1. OCR request/context       -> OCR
# 2. Weather                   -> WEATHER
# 3. Explicit web request      -> WEB
# 4. Greeting                  -> GREETING
# 5. General conversation      -> GENERAL
# 6. Active PDF + normal query -> RAG
#
# The classifier is NOT allowed to send a normal question
# about an active PDF to WEB.
#
# This is intentional.
# =========================================================


VALID_ROUTES = {
    "rag",
    "web",
    "weather",
    "ocr",
    "greeting",
    "general",
}


# =========================================================
# EXPLICIT WEB REQUEST
# =========================================================

def is_explicit_web_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    if not q:
        return False

    web_patterns = (
        "search the web",
        "search web",
        "search the internet",
        "search online",
        "look it up online",
        "look it up on the internet",
        "find it online",
        "google it",
        "browse the web",
        "browse online",

        "latest",
        "latest news",
        "today's news",
        "today news",
        "current news",
        "breaking news",
        "recent news",

        "what happened today",
        "what is happening today",
        "current information",
        "current status",
        "live information",
    )

    return any(
        pattern in q
        for pattern in web_patterns
    )


# =========================================================
# GENERAL / CONVERSATIONAL REQUEST
# =========================================================

def is_general_request(
    query: str,
) -> bool:

    q = (
        query or ""
    ).strip().lower()

    general_patterns = (
        "how are you",
        "who are you",
        "what can you do",
        "help me",
        "thank you",
        "thanks",
        "bye",
        "goodbye",
    )

    return any(
        pattern in q
        for pattern in general_patterns
    )


# =========================================================
# SUPERVISOR
# =========================================================

def supervisor(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    selected_document = (
        state.get(
            "selected_document",
            "",
        )
        or ""
    ).strip()

    document_context = bool(
        state.get(
            "document_context",
            False,
        )
    )

    ocr_text = (
        state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    history = state.get(
        "history",
        [],
    )

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,
            "route": "general",
            "answer": "",
            "sources": [],
        }

    # =====================================================
    # DEBUG INPUT
    # =====================================================

    print(
        "\n================ SUPERVISOR ================"
    )

    print(
        "User query:",
        query,
    )

    print(
        "Selected document:",
        selected_document or "NONE",
    )

    print(
        "Document context:",
        document_context,
    )

    print(
        "OCR available:",
        bool(ocr_text),
    )

    # =====================================================
    # 1. OCR
    # =====================================================

    if ocr_text:

        route = "ocr"

        print(
            "[SUPERVISOR] OCR context detected -> OCR"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": document_context,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 2. WEATHER
    # =====================================================

    q = query.lower()

    weather_words = {
        "weather",
        "temperature",
        "forecast",
        "rain",
        "raining",
        "snow",
        "humidity",
    }

    if any(
        word in q
        for word in weather_words
    ):

        route = "weather"

        print(
            "[SUPERVISOR] Weather request -> WEATHER"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": document_context,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 3. EXPLICIT WEB REQUEST
    #
    # IMPORTANT:
    #
    # Only an explicit request for online/current
    # information is allowed to use WEB.
    # =====================================================

    if is_explicit_web_request(
        query
    ):

        route = "web"

        print(
            "[SUPERVISOR] Explicit web request -> WEB"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": document_context,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 4. GREETING
    # =====================================================

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "wassup",
        "what's up",
        "whats up",
    }

    if q in greetings:

        route = "greeting"

        print(
            "[SUPERVISOR] Greeting -> GREETING"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": document_context,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 5. GENERAL CONVERSATION
    # =====================================================

    if is_general_request(
        query
    ):

        route = "general"

        print(
            "[SUPERVISOR] General conversation -> GENERAL"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": document_context,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 6. ACTIVE DOCUMENT
    #
    # THIS IS THE CRITICAL FIX.
    #
    # If a document is selected, ALL remaining normal
    # questions go to RAG.
    #
    # We do NOT ask the LLM whether it should be RAG.
    #
    # Example:
    #
    # Selected:
    #     Ayushman Bharat Yojna.pdf
    #
    # User:
    #     What is Ayushman Bharat Yojana?
    #
    # -> RAG
    #
    # User:
    #     What are the benefits?
    #
    # -> RAG
    #
    # User:
    #     What are the schemes?
    #
    # -> RAG
    #
    # User:
    #     Summarize this document.
    #
    # -> RAG
    # =====================================================

    if selected_document and document_context:

        route = "rag"

        print(
            "[SUPERVISOR] Active document -> RAG"
        )

        print(
            "[SUPERVISOR] Classifier bypassed for document query."
        )

        print(
            "=============================================\n"
        )

        return {
            **state,
            "route": route,
            "selected_document": selected_document,
            "document_context": True,
            "ocr_text": ocr_text,
            "history": history,
        }

    # =====================================================
    # 7. NO DOCUMENT
    #
    # Only here do we allow the classifier/LLM to decide
    # between general, web, etc.
    # =====================================================

    try:

        route = classify_intent(
            query=query,
            history=history,
            ocr_text=ocr_text,
            selected_document="",
            document_context=False,
        )

        route = (
            route or "general"
        ).strip().lower()

    except Exception as error:

        print(
            "[SUPERVISOR CLASSIFIER ERROR]",
            repr(error),
        )

        route = "general"

    # =====================================================
    # CLEAN ROUTE
    # =====================================================

    route = (
        route
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
        .strip()
        .lower()
    )

    if route not in VALID_ROUTES:

        print(
            "[SUPERVISOR] Invalid classifier route:",
            route,
        )

        route = "general"

    # =====================================================
    # FINAL DEBUG
    # =====================================================

    print(
        "[SUPERVISOR] Final decision:",
        route,
    )

    print(
        "=============================================\n"
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {
        **state,
        "route": route,
        "selected_document": selected_document,
        "document_context": document_context,
        "ocr_text": ocr_text,
        "history": history,
    }