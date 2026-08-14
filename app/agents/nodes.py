# from app.agents.state import AgentState

# from app.rag.document_rag import document_rag
# from app.rag.retriever import retrieve

# from app.llm.gemini import llm


# # =========================================================
# # CONFIG
# # =========================================================

# RAG_RELEVANCE_THRESHOLD = 0.45


# # =========================================================
# # SAFE HISTORY
# # =========================================================

# def safe_history(
#     state: AgentState,
# ) -> list[dict]:

#     history = state.get(
#         "history",
#         [],
#     )

#     if not isinstance(
#         history,
#         list,
#     ):
#         return []

#     return history


# # =========================================================
# # DOCUMENT RETRIEVAL
# # =========================================================

# def get_document_matches(
#     query: str,
#     selected_document: str,
# ):

#     if not query or not selected_document:
#         return []

#     try:

#         matches = retrieve(
#             query=query,
#             top_k=5,
#             selected_document=selected_document,
#         )

#         if not matches:
#             return []

#         return matches

#     except Exception as error:

#         print(
#             "[RAG RETRIEVAL ERROR]",
#             repr(error),
#         )

#         return []


# # =========================================================
# # BEST DOCUMENT RELEVANCE
# # =========================================================

# def get_best_document_score(
#     matches,
# ) -> float:

#     best_score = 0.0

#     for match in matches or []:

#         if not isinstance(
#             match,
#             dict,
#         ):
#             continue

#         try:

#             score = float(
#                 match.get(
#                     "score",
#                     0.0,
#                 )
#             )

#             best_score = max(
#                 best_score,
#                 score,
#             )

#         except (
#             TypeError,
#             ValueError,
#         ):

#             continue

#     return best_score


# # =========================================================
# # RAG NODE
# #
# # FLOW
# #
# # Supervisor
# #      |
# #      v
# #     RAG
# #      |
# #      v
# # Retrieve selected document
# #      |
# #      v
# # Relevance score
# #      |
# #      +----------------------+
# #      |                      |
# #   HIGH SCORE            LOW SCORE
# #      |                      |
# #      v                      v
# #  Document RAG              WEB
# #      |                      |
# #      v                      v
# #  Answer + Sources      Answer + Sources
# #
# # IMPORTANT:
# #
# # RAG does NOT blindly answer.
# # If the selected document does not contain enough
# # relevant information, WEB is used as fallback.
# # =========================================================

# def rag_node(
#     state: AgentState,
# ) -> AgentState:

#     query = (
#         state.get(
#             "query",
#             "",
#         )
#         or ""
#     ).strip()

#     selected_document = (
#         state.get(
#             "selected_document",
#             "",
#         )
#         or ""
#     ).strip()

#     history = safe_history(
#         state
#     )

#     if not query:

#         return {
#             **state,
#             "route": "rag",
#             "answer": "",
#             "sources": [],
#         }

#     # =====================================================
#     # NO DOCUMENT
#     # =====================================================

#     if not selected_document:

#         print(
#             "[RAG] No selected document -> GENERAL"
#         )

#         return general_node(
#             {
#                 **state,
#                 "route": "general",
#             }
#         )

#     print(
#         "\n================ RAG NODE ================"
#     )

#     print(
#         "Query:",
#         query,
#     )

#     print(
#         "Selected document:",
#         selected_document,
#     )

#     # =====================================================
#     # RETRIEVE
#     # =====================================================

#     matches = get_document_matches(
#         query=query,
#         selected_document=selected_document,
#     )

#     best_score = get_best_document_score(
#         matches
#     )

#     print(
#         "Retrieved chunks:",
#         len(matches),
#     )

#     print(
#         "Best relevance:",
#         best_score,
#     )

#     # =====================================================
#     # DOCUMENT DOES NOT HAVE ENOUGH INFORMATION
#     #
#     # IMPORTANT:
#     #
#     # FALL BACK TO WEB.
#     # =====================================================

#     if not matches or best_score < RAG_RELEVANCE_THRESHOLD:

#         print(
#             "[RAG] Document insufficient."
#         )

#         print(
#             "[RAG] Falling back to WEB."
#         )

#         return web_node(
#             {
#                 **state,
#                 "route": "web",
#                 "fallback_reason": (
#                     "Selected document did not "
#                     "contain sufficiently relevant information."
#                 ),
#                 "rag_relevance_score": best_score,
#             }
#         )

#     # =====================================================
#     # DOCUMENT HAS RELEVANT INFORMATION
#     # =====================================================

#     print(
#         "[RAG] Relevant document chunks found."
#     )

#     try:

#         result = document_rag(
#             query=query,
#             selected_document=selected_document,
#             history=history,
#         )

#     except Exception as error:

#         print(
#             "[RAG ANSWER ERROR]",
#             repr(error),
#         )

#         # =================================================
#         # RAG GENERATION FAILED
#         #
#         # WEB FALLBACK
#         # =================================================

#         print(
#             "[RAG] Generation failed -> WEB fallback."
#         )

#         return web_node(
#             {
#                 **state,
#                 "route": "web",
#                 "fallback_reason": (
#                     "Document retrieval succeeded "
#                     "but document answer generation failed."
#                 ),
#                 "rag_relevance_score": best_score,
#             }
#         )

#     # =====================================================
#     # INVALID RESULT
#     # =====================================================

#     if not isinstance(
#         result,
#         dict,
#     ):

#         return web_node(
#             {
#                 **state,
#                 "route": "web",
#             }
#         )

#     answer = (
#         result.get(
#             "answer",
#             "",
#         )
#         or ""
#     ).strip()

#     sources = (
#         result.get(
#             "sources",
#             [],
#         )
#         or []
#     )

#     if not sources:

#         sources = matches

#     # =====================================================
#     # DOCUMENT_RAG SAYS NOT RELEVANT
#     # =====================================================

#     relevant = result.get(
#         "relevant",
#         None,
#     )

#     if relevant is False:

#         print(
#             "[RAG] document_rag says insufficient."
#         )

#         print(
#             "[RAG] Falling back to WEB."
#         )

#         return web_node(
#             {
#                 **state,
#                 "route": "web",
#                 "fallback_reason": (
#                     "Document RAG determined that "
#                     "the document did not contain enough information."
#                 ),
#                 "rag_relevance_score": best_score,
#             }
#         )

#     # =====================================================
#     # EMPTY ANSWER
#     # =====================================================

#     if not answer:

#         print(
#             "[RAG] Empty answer -> WEB fallback."
#         )

#         return web_node(
#             {
#                 **state,
#                 "route": "web",
#                 "fallback_reason": (
#                     "Document retrieval succeeded "
#                     "but no answer was generated."
#                 ),
#                 "rag_relevance_score": best_score,
#             }
#         )

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     print(
#         "[RAG] SUCCESS"
#     )

#     print(
#         "RAG relevance:",
#         best_score,
#     )

#     print(
#         "RAG sources:",
#         len(sources),
#     )

#     print(
#         "==========================================\n"
#     )

#     return {
#         **state,
#         "route": "rag",
#         "answer": answer,
#         "sources": sources,
#         "selected_document": selected_document,
#         "document_context": True,
#         "relevance_score": best_score,
#     }

# # =========================================================
# # GENERAL AI NODE
# #
# # Used when the supervisor determines that the question
# # is unrelated to the selected document and does not
# # require web/current information.
# # =========================================================

# def general_node(
#     state: AgentState,
# ) -> AgentState:

#     query = (
#         state.get(
#             "query",
#             "",
#         )
#         or ""
#     ).strip()

#     history = safe_history(
#         state
#     )

#     if not query:

#         return {
#             **state,
#             "route": "general",
#             "answer": "",
#             "sources": [],
#         }

#     history_parts = []

#     for message in history[-5:]:

#         if not isinstance(
#             message,
#             dict,
#         ):
#             continue

#         role = str(
#             message.get(
#                 "role",
#                 "user",
#             )
#         )

#         content = str(
#             message.get(
#                 "content",
#                 "",
#             )
#         ).strip()

#         if content:

#             history_parts.append(
#                 f"{role.upper()}: {content}"
#             )

#     history_text = (
#         "\n".join(history_parts)
#         if history_parts
#         else "No previous conversation."
#     )

#     prompt = f"""
# You are a helpful general-purpose AI assistant.

# Conversation:
# {history_text}

# User:
# {query}

# Answer the user directly and naturally.

# Do not mention:
# - RAG
# - Pinecone
# - routing
# - internal tools
# - system architecture
# """

#     # =====================================================
#     # PRIMARY: LLM
#     # =====================================================

#     try:

#         print(
#             "\n================ GENERAL LLM ================"
#         )

#         print(
#             "Query:",
#             query,
#         )

#         answer = llm.generate(
#             prompt
#         )

#         answer = (
#             answer or ""
#         ).strip()

#         if answer:

#             print(
#                 "[GENERAL] LLM SUCCESS"
#             )

#             print(
#                 "=============================================\n"
#             )

#             return {
#                 **state,
#                 "route": "general",
#                 "answer": answer,
#                 "sources": [],
#             }

#         print(
#             "[GENERAL] LLM returned empty answer."
#         )

#     except Exception as error:

#         print(
#             "[GENERAL LLM ERROR]",
#             repr(error),
#         )

#     # =====================================================
#     # FALLBACK: WEB
#     # =====================================================

#     print(
#         "[GENERAL] Falling back to WEB."
#     )

#     return web_node(
#         {
#             **state,
#             "route": "web",
#             "fallback_reason": (
#                 "General LLM failed to generate an answer."
#             ),
#         }
#     )

# # =========================================================
# # GREETING NODE
# # =========================================================

# def greeting_node(
#     state: AgentState,
# ) -> AgentState:

#     return {
#         **state,
#         "route": "greeting",
#         "answer": (
#             "Hello! 👋 How can I help you today?"
#         ),
#         "sources": [],
#     }


# # =========================================================
# # WEB SEARCH NODE
# #
# # Used when:
# #
# # 1. Supervisor chooses WEB
# # OR
# # 2. RAG finds insufficient document information
# #
# # Web answer should contain sources returned by the
# # web search tool.
# # =========================================================

# def web_node(
#     state: AgentState,
# ) -> AgentState:

#     query = (
#         state.get(
#             "query",
#             "",
#         )
#         or ""
#     ).strip()

#     if not query:

#         return {
#             **state,
#             "route": "web",
#             "answer": "",
#             "sources": [],
#         }

#     print(
#         "\n================ WEB NODE ================"
#     )

#     print(
#         "Query:",
#         query,
#     )

#     try:

#         from app.tools.web_search_tool import (
#             web_search,
#         )

#         result = web_search(
#             query=query,
#             max_results=5,
#         )

#         # =================================================
#         # INVALID RESULT
#         # =================================================

#         if not isinstance(
#             result,
#             dict,
#         ):

#             return {
#                 **state,
#                 "route": "web",
#                 "answer": str(result),
#                 "sources": [],
#             }

#         answer = (
#             result.get(
#                 "answer",
#                 "",
#             )
#             or ""
#         ).strip()

#         sources = (
#             result.get(
#                 "sources",
#                 [],
#             )
#             or []
#         )

#         print(
#             "Web sources:",
#             len(sources),
#         )

#         # =================================================
#         # WEB TOOL ALREADY GENERATED ANSWER
#         # =================================================

#         if answer:

#             print(
#                 "[WEB] Search + answer generation SUCCESS."
#             )

#             print(
#                 "==========================================\n"
#             )

#             return {
#                 **state,
#                 "route": "web",
#                 "answer": answer,
#                 "sources": sources,
#             }

#         # =================================================
#         # SOURCES EXIST BUT ANSWER EMPTY
#         #
#         # Generate answer OURSELVES from sources.
#         # =================================================

#         if sources:

#             print(
#                 "[WEB] Sources found but answer empty."
#             )

#             print(
#                 "[WEB] Running fallback LLM synthesis."
#             )

#             source_text = []

#             for index, source in enumerate(
#                 sources[:5],
#                 start=1,
#             ):

#                 if not isinstance(
#                     source,
#                     dict,
#                 ):
#                     continue

#                 title = str(
#                     source.get(
#                         "title",
#                         "",
#                     )
#                 )

#                 snippet = str(
#                     source.get(
#                         "snippet",
#                         source.get(
#                             "content",
#                             source.get(
#                                 "text",
#                                 "",
#                             ),
#                         ),
#                     )
#                 )

#                 url = str(
#                     source.get(
#                         "url",
#                         source.get(
#                             "link",
#                             "",
#                         ),
#                     )
#                 )

#                 source_text.append(
#                     f"""
# SOURCE {index}
# TITLE: {title}
# CONTENT: {snippet}
# URL: {url}
# """
#                 )

#             combined_sources = "\n".join(
#                 source_text
#             )

#             synthesis_prompt = f"""
# You are a helpful AI assistant.

# Answer the user's question using the web
# search results below.

# USER QUESTION:
# {query}

# WEB SEARCH RESULTS:
# {combined_sources}

# Instructions:

# 1. Answer the question directly.
# 2. Use the provided search results as evidence.
# 3. Do not invent facts that are not supported.
# 4. If the results are insufficient, say so.
# 5. Keep the answer clear and useful.
# """

#             try:

#                 generated_answer = llm.generate(
#                     synthesis_prompt
#                 )

#                 generated_answer = (
#                     generated_answer or ""
#                 ).strip()

#                 if generated_answer:

#                     print(
#                         "[WEB] Fallback LLM synthesis SUCCESS."
#                     )

#                     return {
#                         **state,
#                         "route": "web",
#                         "answer": generated_answer,
#                         "sources": sources,
#                     }

#             except Exception as error:

#                 print(
#                     "[WEB FALLBACK LLM ERROR]",
#                     repr(error),
#                 )

#         # =================================================
#         # NOTHING WORKED
#         # =================================================

#         return {
#             **state,
#             "route": "web",
#             "answer": (
#                 "I found web results, but I "
#                 "couldn't generate a reliable answer "
#                 "from them right now."
#             ),
#             "sources": sources,
#         }

#     except Exception as error:

#         print(
#             "[WEB NODE ERROR]",
#             repr(error),
#         )

#         return {
#             **state,
#             "route": "web",
#             "answer": (
#                 "I couldn't perform the web "
#                 "search right now."
#             ),
#             "sources": [],
#         }


# # =========================================================
# # WEATHER NODE
# # =========================================================

# def weather_node(
#     state: AgentState,
# ) -> AgentState:

#     query = (
#         state.get(
#             "query",
#             "",
#         )
#         or ""
#     ).strip()

#     if not query:

#         return {
#             **state,
#             "route": "weather",
#             "answer": "",
#             "sources": [],
#         }

#     try:

#         from app.tools.weather_tool import (
#             get_weather,
#         )

#         # =================================================
#         # EXTRACT LOCATION
#         # =================================================

#         location_prompt = f"""
# Extract the city or location from this weather question.

# Return ONLY the city or location name.

# QUESTION:
# {query}
# """

#         city = llm.generate(
#             location_prompt
#         )

#         city = (
#             city
#             .replace(
#                 '"',
#                 "",
#             )
#             .replace(
#                 "'",
#                 "",
#             )
#             .strip()
#         )

#         if not city:

#             return {
#                 **state,
#                 "route": "weather",
#                 "answer": (
#                     "Please specify a city or "
#                     "location for the weather request."
#                 ),
#                 "sources": [],
#             }

#         # =================================================
#         # WEATHER API
#         # =================================================

#         result = get_weather(
#             city
#         )

#         if not isinstance(
#             result,
#             dict,
#         ):

#             return {
#                 **state,
#                 "route": "weather",
#                 "answer": str(result),
#                 "sources": [],
#             }

#         return {
#             **state,
#             "route": "weather",
#             "answer": (
#                 result.get(
#                     "answer",
#                     "",
#                 )
#                 or ""
#             ),
#             "sources": (
#                 result.get(
#                     "sources",
#                     [],
#                 )
#                 or []
#             ),
#         }

#     except Exception as error:

#         print(
#             "[WEATHER NODE ERROR]",
#             repr(error),
#         )

#         return {
#             **state,
#             "route": "weather",
#             "answer": (
#                 "I couldn't retrieve the weather "
#                 "right now."
#             ),
#             "sources": [],
#         }


# # =========================================================
# # OCR NODE
# # =========================================================

# def ocr_node(
#     state: AgentState,
# ) -> AgentState:

#     query = (
#         state.get(
#             "query",
#             "",
#         )
#         or ""
#     ).strip()

#     ocr_text = (
#         state.get(
#             "ocr_text",
#             "",
#         )
#         or ""
#     ).strip()

#     history = safe_history(
#         state
#     )

#     if not query:

#         return {
#             **state,
#             "route": "ocr",
#             "answer": "",
#             "sources": [],
#         }

#     if not ocr_text:

#         return {
#             **state,
#             "route": "ocr",
#             "answer": (
#                 "No image text is available. "
#                 "Please upload an image first."
#             ),
#             "sources": [],
#         }

#     history_parts = []

#     for message in history[-5:]:

#         if not isinstance(
#             message,
#             dict,
#         ):
#             continue

#         role = str(
#             message.get(
#                 "role",
#                 "user",
#             )
#         )

#         content = str(
#             message.get(
#                 "content",
#                 "",
#             )
#         ).strip()

#         if content:

#             history_parts.append(
#                 f"{role.upper()}: {content}"
#             )

#     history_text = (
#         "\n".join(history_parts)
#         if history_parts
#         else "No previous conversation."
#     )

#     prompt = f"""
# You are answering a question about an uploaded image.

# IMAGE OCR TEXT:
# {ocr_text}

# CONVERSATION HISTORY:
# {history_text}

# USER QUESTION:
# {query}

# Answer ONLY using the OCR text.

# If the answer is not present in the OCR text,
# say that it cannot be found in the image.

# Do not use outside knowledge.
# """

#     try:

#         answer = llm.generate(
#             prompt
#         )

#     except Exception as error:

#         print(
#             "[OCR ERROR]",
#             repr(error),
#         )

#         answer = (
#             "I couldn't generate an answer "
#             "from the image."
#         )

#     return {
#         **state,
#         "route": "ocr",
#         "answer": answer,
#         "sources": [],
#     }


# # =========================================================
# # ROUTE EXECUTION
# # =========================================================

# def route_node(
#     state: AgentState,
# ) -> AgentState:

#     route = (
#         state.get(
#             "route",
#             "general",
#         )
#         or "general"
#     ).strip().lower()

#     print(
#         "[ROUTE NODE] Executing:",
#         route,
#     )

#     if route == "rag":

#         return rag_node(
#             state
#         )

#     if route == "web":

#         return web_node(
#             state
#         )

#     if route == "weather":

#         return weather_node(
#             state
#         )

#     if route == "ocr":

#         return ocr_node(
#             state
#         )

#     if route == "greeting":

#         return greeting_node(
#             state
#         )

#     return general_node(
#         state
#     )
from app.agents.state import AgentState

from app.rag.document_rag import document_rag
from app.rag.retriever import retrieve

from app.llm.gemini import llm


# =========================================================
# CONFIG
# =========================================================

RAG_RELEVANCE_THRESHOLD = 0.45


# =========================================================
# SAFE HISTORY
# =========================================================

def safe_history(
    state: AgentState,
) -> list[dict]:

    history = state.get(
        "history",
        [],
    )

    if not isinstance(
        history,
        list,
    ):
        return []

    return history


# =========================================================
# DOCUMENT RETRIEVAL
# =========================================================

def get_document_matches(
    query: str,
    selected_document: str,
) -> list[dict]:

    if not query or not selected_document:
        return []

    try:

        matches = retrieve(
            query=query,
            top_k=5,
            selected_document=selected_document,
        )

        if not matches:
            return []

        return matches

    except Exception as error:

        print(
            "[RAG RETRIEVAL ERROR]",
            repr(error),
        )

        return []


# =========================================================
# BEST RELEVANCE SCORE
# =========================================================

def get_best_document_score(
    matches,
) -> float:

    best_score = 0.0

    for match in matches or []:

        if not isinstance(
            match,
            dict,
        ):
            continue

        try:

            score = float(
                match.get(
                    "score",
                    0.0,
                )
            )

            best_score = max(
                best_score,
                score,
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

    return best_score


# =========================================================
# BUILD HISTORY TEXT
# =========================================================

def build_history_text(
    history: list[dict],
) -> str:

    history_parts = []

    for message in history[-5:]:

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
        )

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
# RAG NODE
#
# FLOW
#
# Supervisor
#      |
#      v
#     RAG
#      |
#      v
# Retrieve selected document
#      |
#      v
# Calculate relevance
#      |
#      +----------------------+
#      |                      |
#   relevant              not relevant
#      |                      |
#      v                      v
#  Document RAG              WEB
#      |                      |
#      v                      v
# Answer + sources      Answer + web sources
#
# =========================================================

def rag_node(
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

    history = safe_history(
        state
    )

    # =====================================================
    # EMPTY QUERY
    # =====================================================

    if not query:

        return {
            **state,
            "route": "rag",
            "answer": "",
            "sources": [],
            "relevance_score": 0.0,
        }

    # =====================================================
    # NO DOCUMENT
    #
    # This should normally not happen because supervisor
    # should only route to RAG when a document exists.
    #
    # Still keep this safe.
    # =====================================================

    if not selected_document:

        print(
            "[RAG] No selected document -> GENERAL"
        )

        return general_node(
            {
                **state,
                "route": "general",
            }
        )

    # =====================================================
    # LOGGING
    # =====================================================

    print(
        "\n================ RAG NODE ================"
    )

    print(
        "Query:",
        query,
    )

    print(
        "Selected document:",
        selected_document,
    )

    # =====================================================
    # STEP 1
    # RETRIEVE ONLY FROM SELECTED DOCUMENT
    # =====================================================

    matches = get_document_matches(
        query=query,
        selected_document=selected_document,
    )

    # =====================================================
    # STEP 2
    # CALCULATE BEST RELEVANCE
    # =====================================================

    best_score = get_best_document_score(
        matches
    )

    print(
        "Retrieved chunks:",
        len(matches),
    )

    print(
        "Best relevance score:",
        best_score,
    )

    print(
        "RAG threshold:",
        RAG_RELEVANCE_THRESHOLD,
    )

    # =====================================================
    # STEP 3
    # NO RELEVANT DOCUMENT RESULT
    #
    # If there is a selected document but it does not
    # contain enough information, use WEB.
    # =====================================================

    if not matches:

        print(
            "[RAG] No matching chunks."
        )

        print(
            "[RAG] Falling back to WEB."
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "No relevant chunks were found "
                    "in the selected document."
                ),
                "rag_relevance_score": 0.0,
                "relevance_score": 0.0,
            }
        )

    # =====================================================
    # STEP 4
    # LOW RELEVANCE
    # =====================================================

    if best_score < RAG_RELEVANCE_THRESHOLD:

        print(
            "[RAG] Relevance below threshold."
        )

        print(
            "[RAG] Falling back to WEB."
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "The selected document did not "
                    "contain sufficiently relevant information."
                ),
                "rag_relevance_score": best_score,
                "relevance_score": best_score,
            }
        )

    # =====================================================
    # DOCUMENT IS RELEVANT
    # =====================================================

    print(
        "[RAG] Relevant document chunks found."
    )

    # =====================================================
    # STEP 5
    # GENERATE ANSWER FROM DOCUMENT
    # =====================================================

    try:

        result = document_rag(
            query=query,
            selected_document=selected_document,
            history=history,
        )

    except Exception as error:

        print(
            "[RAG ANSWER ERROR]",
            repr(error),
        )

        # -------------------------------------------------
        # Retrieval succeeded but generation failed.
        #
        # We can safely fall back to WEB.
        # -------------------------------------------------

        print(
            "[RAG] Document generation failed -> WEB"
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "Document retrieval succeeded, "
                    "but document answer generation failed."
                ),
                "rag_relevance_score": best_score,
                "relevance_score": best_score,
            }
        )

    # =====================================================
    # INVALID RESULT
    # =====================================================

    if not isinstance(
        result,
        dict,
    ):

        print(
            "[RAG] Invalid document_rag result."
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "Document RAG returned an invalid result."
                ),
                "rag_relevance_score": best_score,
                "relevance_score": best_score,
            }
        )

    # =====================================================
    # ANSWER
    # =====================================================

    answer = (
        result.get(
            "answer",
            "",
        )
        or ""
    ).strip()

    # =====================================================
    # SOURCES
    # =====================================================

    sources = (
        result.get(
            "sources",
            [],
        )
        or []
    )

    # If document_rag didn't return sources,
    # use the retrieved chunks directly.

    if not sources:

        sources = matches

    # =====================================================
    # DOCUMENT_RAG RELEVANCE
    # =====================================================

    relevant = result.get(
        "relevant",
        None,
    )

    if relevant is False:

        print(
            "[RAG] document_rag says document "
            "is insufficient."
        )

        print(
            "[RAG] Falling back to WEB."
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "Document RAG determined that "
                    "the document does not contain enough information."
                ),
                "rag_relevance_score": best_score,
                "relevance_score": best_score,
            }
        )

    # =====================================================
    # EMPTY ANSWER
    # =====================================================

    if not answer:

        print(
            "[RAG] Document answer is empty."
        )

        print(
            "[RAG] Falling back to WEB."
        )

        return web_node(
            {
                **state,
                "route": "web",
                "fallback_reason": (
                    "Document retrieval succeeded, "
                    "but no document answer was generated."
                ),
                "rag_relevance_score": best_score,
                "relevance_score": best_score,
            }
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        "[RAG] SUCCESS"
    )

    print(
        "RAG relevance:",
        best_score,
    )

    print(
        "RAG sources:",
        len(sources),
    )

    print(
        "==========================================\n"
    )

    return {
        **state,

        "route": "rag",

        "answer": answer,

        "sources": sources,

        "selected_document": selected_document,

        "document_context": True,

        "relevance_score": best_score,
    }


# =========================================================
# GENERAL AI NODE
#
# Used for normal questions that do not require:
# - document retrieval
# - web search
# - weather
# - OCR
# =========================================================

def general_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    if not query:

        return {
            **state,
            "route": "general",
            "answer": "",
            "sources": [],
        }

    history_text = build_history_text(
        history
    )

    prompt = f"""
You are a helpful general-purpose AI assistant.

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{query}

Answer the user's question directly and naturally.

Use your own general knowledge.

Do not mention:
- RAG
- Pinecone
- routing
- internal tools
- system architecture
- document retrieval
"""

    try:

        print(
            "\n================ GENERAL LLM ================"
        )

        print(
            "Query:",
            query,
        )

        answer = llm.generate(
            prompt
        )

        answer = (
            answer or ""
        ).strip()

        if answer:

            print(
                "[GENERAL] LLM SUCCESS"
            )

            print(
                "=============================================\n"
            )

            return {
                **state,
                "route": "general",
                "answer": answer,
                "sources": [],
            }

        print(
            "[GENERAL] LLM returned empty answer."
        )

    except Exception as error:

        print(
            "[GENERAL LLM ERROR]",
            repr(error),
        )

    # =====================================================
    # GENERAL LLM FAILED
    #
    # Use WEB as fallback.
    # =====================================================

    print(
        "[GENERAL] Falling back to WEB."
    )

    return web_node(
        {
            **state,
            "route": "web",
            "fallback_reason": (
                "General LLM failed to generate "
                "an answer."
            ),
        }
    )


# =========================================================
# GREETING NODE
# =========================================================

def greeting_node(
    state: AgentState,
) -> AgentState:

    return {
        **state,
        "route": "greeting",
        "answer": (
            "Hello! 👋 How can I help you today?"
        ),
        "sources": [],
    }


# =========================================================
# WEB SEARCH NODE
#
# Used when:
#
# 1. Supervisor selects WEB
# 2. RAG finds insufficient document information
# 3. General LLM fails
#
# The web_search tool is responsible for:
# - searching the web
# - generating an answer
# - returning sources
# =========================================================

def web_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    if not query:

        return {
            **state,
            "route": "web",
            "answer": "",
            "sources": [],
        }

    print(
        "\n================ WEB NODE ================"
    )

    print(
        "Query:",
        query,
    )

    try:

        from app.tools.web_search_tool import (
            web_search,
        )

        result = web_search(
            query=query,
            max_results=5,
        )

        # =================================================
        # INVALID RESULT
        # =================================================

        if not isinstance(
            result,
            dict,
        ):

            return {
                **state,
                "route": "web",
                "answer": str(result),
                "sources": [],
            }

        # =================================================
        # ANSWER
        # =================================================

        answer = (
            result.get(
                "answer",
                "",
            )
            or ""
        ).strip()

        # =================================================
        # SOURCES
        # =================================================

        sources = (
            result.get(
                "sources",
                [],
            )
            or []
        )

        print(
            "Web sources:",
            len(sources),
        )

        # =================================================
        # WEB SEARCH SUCCESS
        # =================================================

        if answer:

            print(
                "[WEB] Search + answer generation SUCCESS."
            )

            print(
                "==========================================\n"
            )

            return {
                **state,
                "route": "web",
                "answer": answer,
                "sources": sources,
            }

        # =================================================
        # SOURCES EXIST BUT ANSWER EMPTY
        # =================================================

        if sources:

            print(
                "[WEB] Sources found but answer empty."
            )

            source_text = []

            for index, source in enumerate(
                sources[:5],
                start=1,
            ):

                if not isinstance(
                    source,
                    dict,
                ):
                    continue

                title = str(
                    source.get(
                        "title",
                        "",
                    )
                )

                snippet = str(
                    source.get(
                        "snippet",
                        source.get(
                            "content",
                            source.get(
                                "text",
                                "",
                            ),
                        ),
                    )
                )

                url = str(
                    source.get(
                        "url",
                        source.get(
                            "link",
                            "",
                        ),
                    )
                )

                source_text.append(
                    f"""
SOURCE {index}

TITLE:
{title}

CONTENT:
{snippet}

URL:
{url}
"""
                )

            combined_sources = "\n".join(
                source_text
            )

            synthesis_prompt = f"""
You are a helpful AI assistant.

USER QUESTION:
{query}

WEB SEARCH RESULTS:
{combined_sources}

Answer the user's question using ONLY
the information contained in the web search results.

Rules:

1. Give a direct answer.
2. Use the search results as evidence.
3. Do not invent unsupported facts.
4. If the results are insufficient, say so.
5. Do not mention internal routing.
6. Do not mention RAG or Pinecone.
"""

            try:

                generated_answer = llm.generate(
                    synthesis_prompt
                )

                generated_answer = (
                    generated_answer or ""
                ).strip()

                if generated_answer:

                    print(
                        "[WEB] Fallback synthesis SUCCESS."
                    )

                    return {
                        **state,
                        "route": "web",
                        "answer": generated_answer,
                        "sources": sources,
                    }

            except Exception as error:

                print(
                    "[WEB FALLBACK LLM ERROR]",
                    repr(error),
                )

        # =================================================
        # NOTHING WORKED
        # =================================================

        return {
            **state,
            "route": "web",
            "answer": (
                "I found web results, but I "
                "couldn't generate a reliable answer "
                "from them right now."
            ),
            "sources": sources,
        }

    except Exception as error:

        print(
            "[WEB NODE ERROR]",
            repr(error),
        )

        return {
            **state,
            "route": "web",
            "answer": (
                "I couldn't perform the web "
                "search right now."
            ),
            "sources": [],
        }


# =========================================================
# WEATHER NODE
# =========================================================

def weather_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    if not query:

        return {
            **state,
            "route": "weather",
            "answer": "",
            "sources": [],
        }

    try:

        from app.tools.weather_tool import (
            get_weather,
        )

        # =================================================
        # EXTRACT LOCATION
        # =================================================

        location_prompt = f"""
Extract the city or location from this weather question.

Return ONLY the city or location name.

QUESTION:
{query}
"""

        city = llm.generate(
            location_prompt
        )

        city = (
            city
            .replace(
                '"',
                "",
            )
            .replace(
                "'",
                "",
            )
            .strip()
        )

        if not city:

            return {
                **state,
                "route": "weather",
                "answer": (
                    "Please specify a city or "
                    "location for the weather request."
                ),
                "sources": [],
            }

        # =================================================
        # WEATHER API
        # =================================================

        result = get_weather(
            city
        )

        if not isinstance(
            result,
            dict,
        ):

            return {
                **state,
                "route": "weather",
                "answer": str(result),
                "sources": [],
            }

        return {
            **state,
            "route": "weather",
            "answer": (
                result.get(
                    "answer",
                    "",
                )
                or ""
            ),
            "sources": (
                result.get(
                    "sources",
                    [],
                )
                or []
            ),
        }

    except Exception as error:

        print(
            "[WEATHER NODE ERROR]",
            repr(error),
        )

        return {
            **state,
            "route": "weather",
            "answer": (
                "I couldn't retrieve the weather "
                "right now."
            ),
            "sources": [],
        }


# =========================================================
# OCR NODE
# =========================================================

def ocr_node(
    state: AgentState,
) -> AgentState:

    query = (
        state.get(
            "query",
            "",
        )
        or ""
    ).strip()

    ocr_text = (
        state.get(
            "ocr_text",
            "",
        )
        or ""
    ).strip()

    history = safe_history(
        state
    )

    if not query:

        return {
            **state,
            "route": "ocr",
            "answer": "",
            "sources": [],
        }

    if not ocr_text:

        return {
            **state,
            "route": "ocr",
            "answer": (
                "No image text is available. "
                "Please upload an image first."
            ),
            "sources": [],
        }

    history_text = build_history_text(
        history
    )

    prompt = f"""
You are answering a question about an uploaded image.

IMAGE OCR TEXT:
{ocr_text}

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{query}

Answer ONLY using the OCR text.

If the answer is not present in the OCR text,
say that it cannot be found in the image.

Do not use outside knowledge.
"""

    try:

        answer = llm.generate(
            prompt
        )

    except Exception as error:

        print(
            "[OCR ERROR]",
            repr(error),
        )

        answer = (
            "I couldn't generate an answer "
            "from the image."
        )

    return {
        **state,
        "route": "ocr",
        "answer": answer,
        "sources": [],
    }


# =========================================================
# ROUTE EXECUTION
# =========================================================

def route_node(
    state: AgentState,
) -> AgentState:

    route = (
        state.get(
            "route",
            "general",
        )
        or "general"
    ).strip().lower()

    print(
        "[ROUTE NODE] Executing:",
        route,
    )

    if route == "rag":

        return rag_node(
            state
        )

    if route == "web":

        return web_node(
            state
        )

    if route == "weather":

        return weather_node(
            state
        )

    if route == "ocr":

        return ocr_node(
            state
        )

    if route == "greeting":

        return greeting_node(
            state
        )

    return general_node(
        state
    )