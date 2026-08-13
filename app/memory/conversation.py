def add_message(history: list[dict], role: str, content: str) -> list[dict]:
    return [*history, {"role": role, "content": content}]
