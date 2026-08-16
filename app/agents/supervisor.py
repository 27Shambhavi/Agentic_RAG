from app.agents.state import AgentState
from app.agents.classifier import classify_intent


# =========================================================
# VALID ROUTES
# =========================================================

VALID_ROUTES = {
    "rag",
    "web_rag",
    "web",
    "weather",
    "ocr",
    "greeting",
    "general",
}


# =========================================================
# GREETING
# =========================================================

def is_greeting(query: str) -> bool:

    q = (
        query or ""
    ).strip().lower()

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "wassup",
        "what's up",
        "whats up",
    }

    return q in greetings


# =========================================================
# WEATHER
# =========================================================

def is_weather_request(query: str) -> bool:

    q = (
        query or ""
    ).strip().lower()

    weather_words = {
        "weather",
        "temperature",
        "forecast",
        "rain",
        "raining",
        "snow",
        "humidity",
    }

    return any(
        word in q
        for word in weather_words
    )


# =========================================================
# EXPLICIT WEB SEARCH
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
# URL DETECTION
# =========================================================

def extract_url(
    query: str,
) -> str:

    import re

    q = (
        query or ""
    ).strip()

    pattern = r"https?://[^\s<>\"']+"

    match = re.search(
        pattern,
        q,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    return (
        match.group(0)
        .rstrip(".,!?;:)]}")
        .strip()
    )


# =========================================================
# SUPERVISOR
# =========================================================

def supervisor(
    state: AgentState,
) -> AgentState:

    # =====================================================
    # INPUT
    # =====================================================

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

    web_url = (
        state.get(
            "web_url",
            "",
        )
        or ""
    ).strip()

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
    # DEBUG
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

    print(
        "State Web URL:",
        web_url or "NONE",
    )

    # =====================================================
    # 1. EXPLICIT URL
    # =====================================================
    #
    # URL MUST ALWAYS become WEB RAG.
    #
    # This happens before classifier.
    # =====================================================

    detected_url = extract_url(
        query
    )

    if detected_url:

        print(
            "[SUPERVISOR] URL detected -> WEB RAG"
        )

        print(
            "URL:",
            detected_url,
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "web_rag",

            "web_url": detected_url,

            "web_context": True,
        }

    # =====================================================
    # If frontend already supplied URL
    # =====================================================

    if web_url:

        print(
            "[SUPERVISOR] Existing web URL -> WEB RAG"
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "web_rag",

            "web_url": web_url,

            "web_context": True,
        }

    # =====================================================
    # 2. OCR
    # =====================================================

    if ocr_text:

        print(
            "[SUPERVISOR] OCR context -> OCR"
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "ocr",

            "ocr_text": ocr_text,
        }

    # =====================================================
    # 3. WEATHER
    # =====================================================

    if is_weather_request(
        query
    ):

        print(
            "[SUPERVISOR] Weather -> WEATHER"
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "weather",
        }

    # =====================================================
    # 4. GREETING
    # =====================================================

    if is_greeting(
        query
    ):

        print(
            "[SUPERVISOR] Greeting -> GREETING"
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "greeting",
        }

    # =====================================================
    # 5. EXPLICIT WEB SEARCH
    # =====================================================

    if is_explicit_web_request(
        query
    ):

        print(
            "[SUPERVISOR] Explicit web request -> WEB"
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "web",
        }

    # =====================================================
    # 6. ACTIVE PDF
    # =====================================================
    #
    # THIS IS IMPORTANT.
    #
    # If a PDF is selected, normal questions go to RAG.
    #
    # This prevents the classifier from accidentally
    # sending PDF questions to WEB.
    # =====================================================

    if (
        selected_document
        and document_context
    ):

        print(
            "[SUPERVISOR] Active PDF -> RAG"
        )

        print(
            "[SUPERVISOR] Classifier bypassed."
        )

        print(
            "=============================================\n"
        )

        return {
            **state,

            "route": "rag",

            "selected_document": selected_document,

            "document_context": True,
        }

    # =====================================================
    # 7. NO SPECIAL CONTEXT
    # =====================================================
    #
    # ONLY NOW do we ask the classifier.
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
            route
            or "general"
        ).strip().lower()

    except Exception as error:

        print(
            "[SUPERVISOR CLASSIFIER ERROR]"
        )

        print(
            repr(error)
        )

        route = "general"

    # =====================================================
    # CLEAN
    # =====================================================

    route = (
        route
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
        .strip()
        .lower()
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    if route not in VALID_ROUTES:

        print(
            "[SUPERVISOR] Invalid route:",
            route,
        )

        route = "general"

    # =====================================================
    # FINAL
    # =====================================================

    print(
        "[SUPERVISOR] Final decision:",
        route,
    )

    print(
        "=============================================\n"
    )

    return {
        **state,

        "route": route,

        "selected_document": selected_document,

        "document_context": document_context,

        "ocr_text": ocr_text,

        "history": history,

        "web_url": web_url,
    }