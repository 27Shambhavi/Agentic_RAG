from typing import TypedDict


class AgentState(TypedDict, total=False):

    query: str

    route: str

    selected_document: str
    document_context: bool

    history: list[dict]

    ocr_text: str

    answer: str
    sources: list

    weather_data: dict
    web_results: list