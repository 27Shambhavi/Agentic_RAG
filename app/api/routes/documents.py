from pathlib import Path
import shutil
import uuid
import re

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import FileResponse

from app.rag.indexer import index_pdf


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CREATE SAFE STORAGE NAME
# =========================================================

def create_storage_name(original_filename: str) -> str:

    original_path = Path(original_filename)

    stem = original_path.stem
    extension = original_path.suffix.lower()

    # Remove unsafe characters
    safe_stem = re.sub(
        r"[^a-zA-Z0-9_\- ]",
        "",
        stem
    ).strip()

    if not safe_stem:
        safe_stem = "document"

    # UUID is only for internal uniqueness
    unique_id = uuid.uuid4().hex

    return f"{unique_id}_{safe_stem}{extension}"


# =========================================================
# GET DISPLAY NAME
# =========================================================

def get_display_name(filename: str) -> str:

    path = Path(filename)

    stem = path.stem
    extension = path.suffix

    # New format:
    # UUID_original_name.pdf
    if "_" in stem:

        first_part, remaining = stem.split(
            "_",
            1
        )

        # Check whether first part is UUID
        if re.fullmatch(
            r"[a-fA-F0-9]{32}",
            first_part
        ):

            return f"{remaining}{extension}"

    # Old UUID-only files
    if re.fullmatch(
        r"[a-fA-F0-9]{32}",
        stem
    ):

        return "Uploaded Document.pdf"

    # Normal filename
    return filename


# =========================================================
# UPLOAD
# =========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    storage_name = create_storage_name(
        file.filename
    )

    file_path = (
        UPLOAD_DIR / storage_name
    )

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        result = index_pdf(
            str(file_path)
        )

        return {
            "status": "success",
            "filename": file.filename,
            "stored_as": storage_name,
            "display_name": file.filename,
            "pages": result["pages"],
            "chunks": result["chunks"],
        }

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# LIST DOCUMENTS
# =========================================================

@router.get("/")
def list_documents():

    documents = []

    for file in sorted(
        UPLOAD_DIR.glob("*.pdf")
    ):

        documents.append(
            {
                "filename": file.name,

                "display_name": get_display_name(
                    file.name
                ),

                "size_kb": round(
                    file.stat().st_size / 1024,
                    2
                ),
            }
        )

    return {
        "documents": documents
    }


# =========================================================
# OPEN PDF
# =========================================================

@router.get("/view/{filename}")
def view_document(
    filename: str
):

    safe_filename = Path(
        filename
    ).name

    file_path = (
        UPLOAD_DIR / safe_filename
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline"
        },
    )