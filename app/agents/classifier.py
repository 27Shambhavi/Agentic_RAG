from app.llm.gemini import llm


CLASSIFIER_PROMPT = """
You are an intent classifier for an AI assistant.

Return exactly ONE route:

greeting
rag
web
general

Classify by the user's intent, not by individual keywords.

RAG:
Use rag when the user is asking about an uploaded document.

Examples:
- What is this report about?
- Summarize this PDF.
- What are the benefits mentioned in the document?
- According to the report, what is PM-JAY?
- Who is the author of this report?

WEB:
Use web when the user needs current or external information.

Examples:
- What is the price of iPhone 17?
- What is today's news?
- Who is the current CEO of Microsoft?
- What is the weather in Delhi?

GENERAL:
Use general for normal questions that don't require the
uploaded document or current web information.

Examples:
- What is Python?
- Explain inheritance.
- What is machine learning?

GREETING:
Use greeting for simple greetings.

Examples:
- Hi
- Hello
- Good morning

IMPORTANT:
A selected PDF does NOT automatically mean RAG.

Only use RAG when the user's question is actually about
the uploaded document.

USER QUERY:
{query}

ROUTE:
"""


def classify_intent(query: str) -> str:

    prompt = CLASSIFIER_PROMPT.format(
        query=query
    )

    result = llm.generate(prompt)

    route = (
        result
        .strip()
        .lower()
        .replace("`", "")
    )

    allowed_routes = {
        "rag",
        "web",
        "general",
        "greeting",
    }

    if route not in allowed_routes:
        return "general"

    return route