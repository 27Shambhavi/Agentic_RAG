from app.llm.gemini import llm
from app.agents.prompts import SUPERVISOR_PROMPT


VALID_ROUTES = {
    "greeting",
    "rag",
    "web",
    "weather",
    "general",
    "ocr",
}


def classify_intent(
    query: str,
    history: list[dict] | None = None,
    ocr_text: str = "",
    selected_document: str = "",
    document_context: bool = False,
) -> str:

    query = (query or "").strip()
    history = history or []

    if not query:
        return "general"

    q = query.lower().strip()

    # =====================================================
    # 1. GREETING
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
        return "greeting"

    # =====================================================
    # 2. WEATHER
    # =====================================================

    weather_words = {
        "weather",
        "temperature",
        "forecast",
        "rain",
        "raining",
        "snow",
        "humidity",
        "climate",
    }

    if any(
        word in q
        for word in weather_words
    ):
        return "weather"

    # =====================================================
    # 3. OCR
    # =====================================================

    if ocr_text and ocr_text.strip():
        return "ocr"

    # =====================================================
    # 4. NO DOCUMENT
    #
    # No PDF selected:
    #
    # Supervisor decides:
    #     general / web
    # =====================================================

    if not selected_document:

        return classify_without_document(
            query=query,
            history=history,
        )

    # =====================================================
    # DOCUMENT IS SELECTED
    # =====================================================

    print(
        "\n================ DOCUMENT ROUTING ================"
    )

    print(
        "Selected document:",
        selected_document,
    )

    print(
        "Question:",
        query,
    )

    # =====================================================
    # 4A. CLEAR CONVERSATIONAL QUESTIONS
    # =====================================================

    conversational_patterns = (
        "how are you",
        "who are you",
        "what can you do",
        "help me",
        "thank you",
        "thanks",
        "bye",
        "goodbye",
    )

    if any(
        pattern in q
        for pattern in conversational_patterns
    ):

        print(
            "Decision: GENERAL"
        )

        print(
            "=================================================\n"
        )

        return "general"

    # =====================================================
    # 4B. EXPLICIT WEB REQUEST
    #
    # These MUST bypass RAG.
    # =====================================================

    explicit_web_patterns = (
        "search the web",
        "search the internet",
        "search online",
        "look it up online",
        "look it up on the internet",
        "search online for",
        "google this",
        "latest news",
        "current news",
        "breaking news",
        "what is happening today",
        "what's happening today",
        "today's news",
        "recent news",
        "latest information",
        "current information",
    )

    if any(
        pattern in q
        for pattern in explicit_web_patterns
    ):

        print(
            "Decision: WEB"
        )

        print(
            "Reason: Explicit web/current request."
        )

        print(
            "=================================================\n"
        )

        return "web"

    # =====================================================
    # 4C. DOCUMENT IS ACTIVE
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # Do NOT ask the supervisor whether this is RAG
    # or WEB.
    #
    # RAG ALWAYS GETS FIRST CHANCE.
    #
    # If document_rag cannot find enough information,
    # rag_node will fall back to WEB.
    # =====================================================

    print(
        "Decision: RAG"
    )

    print(
        "Reason: Active document gets first retrieval attempt."
    )

    print(
        "=================================================\n"
    )

    return "rag"


# =========================================================
# NO DOCUMENT
# =========================================================

def classify_without_document(
    query: str,
    history: list[dict],
) -> str:

    history_text = "\n".join(
        f"{m.get('role', 'user').upper()}: "
        f"{m.get('content', '')}"
        for m in history[-6:]
        if isinstance(m, dict)
        and m.get("content")
    )

    if not history_text:
        history_text = "No previous conversation."

    prompt = SUPERVISOR_PROMPT.format(
        query=query,
        selected_document="NONE",
        document_context=False,
        ocr_available=False,
        history=history_text,
    )

    print(
        "\n================ SUPERVISOR LLM ================"
    )

    print(
        "Question:",
        query,
    )

    print(
        "No selected document."
    )

    try:

        result = llm.generate(
            prompt
        )

        result = (
            result or ""
        ).strip().lower()

    except Exception as error:

        print(
            "[SUPERVISOR ERROR]",
            repr(error),
        )

        # Without a document, if supervisor fails,
        # web is safer for factual questions.
        return "web"

    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    result = (
        result
        .replace("`", "")
        .replace('"', "")
        .replace("'", "")
        .strip()
    )

    # =====================================================
    # EXACT ROUTE
    # =====================================================

    if result in VALID_ROUTES:

        print(
            "Supervisor decision:",
            result,
        )

        print(
            "=================================================\n"
        )

        return result

    # =====================================================
    # EXTRA MODEL TEXT
    # =====================================================

    for route in (
        "web",
        "general",
        "rag",
        "weather",
        "ocr",
        "greeting",
    ):

        if route in result.split():

            print(
                "Supervisor decision:",
                route,
            )

            return route

    # =====================================================
    # FALLBACK
    # =====================================================

    print(
        "Invalid supervisor result:",
        result,
    )

    print(
        "Fallback: WEB"
    )

    return "web"