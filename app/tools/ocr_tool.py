import base64
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral


# =========================================================
# LOAD .ENV
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE
)


# =========================================================
# CONFIG
# =========================================================

OCR_MODEL = "mistral-ocr-latest"


# =========================================================
# ENCODE IMAGE
# =========================================================

def _encode_image(
    image_path: str
) -> str:

    path = Path(image_path)

    if not path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    mime_type, _ = mimetypes.guess_type(
        path.name
    )

    if not mime_type:
        mime_type = "image/jpeg"

    with open(
        path,
        "rb"
    ) as image_file:

        image_bytes = image_file.read()

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# =========================================================
# MISTRAL OCR
# =========================================================

def process_image_ocr(
    image_path: str
) -> dict:

    api_key = os.getenv(
        "MISTRAL_API_KEY"
    )

    if not api_key:

        raise ValueError(
            f"MISTRAL_API_KEY not found.\n"
            f"Expected .env at:\n"
            f"{ENV_FILE}"
        )

    client = Mistral(
        api_key=api_key
    )

    image_data = _encode_image(
        image_path
    )

    response = client.ocr.process(
        model=OCR_MODEL,

        document={
            "type": "image_url",
            "image_url": image_data,
        },

        include_image_base64=False,

        include_blocks=True,

        confidence_scores_granularity="page",
    )

    pages = getattr(
        response,
        "pages",
        []
    )

    page_results = []

    all_text = []

    for page in pages:

        markdown = getattr(
            page,
            "markdown",
            ""
        )

        page_index = getattr(
            page,
            "index",
            len(page_results)
        )

        page_results.append(
            {
                "page": page_index,
                "text": markdown,
            }
        )

        if markdown:

            all_text.append(
                markdown
            )

    return {
        "text": "\n\n".join(
            all_text
        ).strip(),

        "pages": page_results,

        "model": OCR_MODEL,
    }