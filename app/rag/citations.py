import re
from pathlib import Path

def get_display_name(filename: str) -> str:
    path = Path(filename)
    stem = path.stem
    extension = path.suffix
    if "_" in stem:
        first_part, remaining = stem.split("_", 1)
        if re.fullmatch(r"[a-fA-F0-9]{32}", first_part):
            return f"{remaining}{extension}"
    if re.fullmatch(r"[a-fA-F0-9]{32}", stem):
        return "Uploaded Document.pdf"
    return filename

def format_sources(
    documents: list[dict]
) -> list[dict]:

    sources = []

    for doc in documents:

        sources.append(
            {
                "source": get_display_name(doc["source"]),
                "page": doc["page"],
                "score": round(
                    float(doc["score"]),
                    4
                )
            }
        )

    return sources