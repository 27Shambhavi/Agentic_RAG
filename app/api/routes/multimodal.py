from pathlib import Path
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from pydantic import BaseModel

from app.tools.ocr_tool import (
    process_image_ocr
)

from app.agents.graph import (
    agent
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/multimodal",
    tags=["Multimodal"]
)


# =========================================================
# DIRECTORIES
# =========================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

IMAGE_DIR = (
    PROJECT_ROOT / "data" / "images"
)

IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# ALLOWED IMAGE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


# =========================================================
# OCR ENDPOINT
# =========================================================

@router.post("/ocr")
async def image_ocr(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # VALIDATE FILENAME
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    # -----------------------------------------------------
    # VALIDATE EXTENSION
    # -----------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image type. "
                "Supported types: "
                "PNG, JPG, JPEG, WEBP."
            )
        )

    # -----------------------------------------------------
    # TEMPORARY IMAGE NAME
    # -----------------------------------------------------

    safe_name = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    image_path = (
        IMAGE_DIR / safe_name
    )

    try:

        # -------------------------------------------------
        # READ IMAGE
        # -------------------------------------------------

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )

        # -------------------------------------------------
        # SAVE TEMPORARY IMAGE
        # -------------------------------------------------

        with open(
            image_path,
            "wb"
        ) as image_file:

            image_file.write(
                content
            )

        # -------------------------------------------------
        # MISTRAL OCR
        # -------------------------------------------------

        result = process_image_ocr(
            str(image_path)
        )

        extracted_text = result.get(
            "text",
            ""
        )

        # -------------------------------------------------
        # NO TEXT
        # -------------------------------------------------

        if not extracted_text.strip():

            return {
                "status": "success",

                "filename": file.filename,

                "text": "",

                "pages": result.get(
                    "pages",
                    []
                ),

                "model": result.get(
                    "model",
                    "mistral-ocr-latest"
                ),

                "message": (
                    "OCR completed, but no "
                    "readable text was detected."
                ),
            }

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return {
            "status": "success",

            "filename": file.filename,

            "text": extracted_text,

            "pages": result.get(
                "pages",
                []
            ),

            "model": result.get(
                "model",
                "mistral-ocr-latest"
            ),
        }

    except HTTPException:

        raise

    except Exception as error:

        error_message = str(
            error
        )

        # -------------------------------------------------
        # MISTRAL / OCR QUOTA
        # -------------------------------------------------

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED"
            in error_message
            or "quota"
            in error_message.lower()
        ):

            raise HTTPException(
                status_code=429,
                detail=(
                    "Mistral OCR quota or "
                    "rate limit was reached. "
                    "Please try again later."
                )
            )

        # -------------------------------------------------
        # OTHER OCR ERROR
        # -------------------------------------------------

        raise HTTPException(
            status_code=500,
            detail=(
                f"OCR failed: "
                f"{error_message}"
            )
        )

    finally:

        # -------------------------------------------------
        # DELETE TEMPORARY IMAGE
        # -------------------------------------------------

        if image_path.exists():

            try:

                image_path.unlink()

            except Exception:

                pass


# =========================================================
# IMAGE QUESTION REQUEST
# =========================================================

class ImageQuestionRequest(
    BaseModel
):

    question: str

    image_text: str

    image_filename: str = ""


# =========================================================
# ASK ABOUT IMAGE
# =========================================================

@router.post("/ask-image")
async def ask_image(
    request: ImageQuestionRequest
):

    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    question = (
        request.question
        .strip()
    )

    image_text = (
        request.image_text
        .strip()
    )

    image_filename = (
        request.image_filename
        .strip()
    )

    # -----------------------------------------------------
    # VALIDATE QUESTION
    # -----------------------------------------------------

    if not question:

        raise HTTPException(
            status_code=400,
            detail=(
                "Question cannot be empty."
            )
        )

    # -----------------------------------------------------
    # VALIDATE OCR TEXT
    # -----------------------------------------------------

    if not image_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "Image OCR text is empty. "
                "Run OCR before asking a question."
            )
        )

    try:

        # =================================================
        # SEND IMAGE INFORMATION TO AGENT
        # =================================================

        result = agent.invoke(
            {
                "query": question,

                "image_text": image_text,

                "image_filename": (
                    image_filename
                ),

                "context": image_text,
            }
        )

        # =================================================
        # EXTRACT RESPONSE
        # =================================================

        answer = result.get(
            "answer",
            ""
        )

        route = result.get(
            "route",
            "general"
        )

        sources = result.get(
            "sources",
            []
        )

        # -------------------------------------------------
        # EMPTY ANSWER
        # -------------------------------------------------

        if not answer:

            answer = (
                "I couldn't generate an answer "
                "from the image."
            )

        # =================================================
        # RESPONSE
        # =================================================

        return {
            "status": "success",

            "answer": answer,

            "route": route,

            "sources": sources,

            "image_filename": (
                image_filename
            ),
        }

    except Exception as error:

        error_message = str(
            error
        )

        # =================================================
        # GEMINI QUOTA
        # =================================================

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED"
            in error_message
            or "quota"
            in error_message.lower()
        ):

            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini free-tier quota "
                    "has been exhausted. "
                    "Please wait for the quota "
                    "to reset before asking "
                    "another AI question."
                )
            )

        # =================================================
        # API KEY
        # =================================================

        if (
            "API_KEY" in error_message
            or "api key" in error_message.lower()
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "LLM API configuration error. "
                    "Please check your API key."
                )
            )

        # =================================================
        # OTHER AGENT ERROR
        # =================================================

        raise HTTPException(
            status_code=500,
            detail=(
                f"Image agent failed: "
                f"{error_message}"
            )
        )