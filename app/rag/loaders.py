from pathlib import Path

import pymupdf


def load_pdf(file_path: str) -> list[dict]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported currently."
        )

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text("text").strip()

        if not text:
            continue

        pages.append(
            {
                "text": text,
                "page": page_number + 1,
                "source": path.name,
            }
        )

    document.close()

    return pages