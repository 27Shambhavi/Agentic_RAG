from pathlib import Path
import shutil
import uuid

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

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


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

    # -----------------------------------------------------
    # SAFE STORAGE NAME
    # -----------------------------------------------------

    original_name = Path(
        file.filename
    ).stem

    unique_name = (
        f"{uuid.uuid4().hex}_"
        f"{original_name}.pdf"
    )

    file_path = (
        UPLOAD_DIR / unique_name
    )

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        result = index_pdf(
            str(file_path)
        )

        return {
            "status": "success",
            "filename": file.filename,
            "stored_as": unique_name,
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

    for file in UPLOAD_DIR.glob("*.pdf"):

        filename = file.name

        # Remove UUID prefix for display
        display_name = filename

        if "_" in filename:

            display_name = filename.split(
                "_",
                1
            )[1]

        documents.append(
            {
                "filename": filename,

                "display_name": display_name,

                "size_kb": round(
                    file.stat().st_size / 1024,
                    2,
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

    # Prevent directory traversal
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
            "Content-Disposition": "inline",
        },
    )