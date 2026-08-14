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


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

UPLOAD_DIR = Path(
    "data/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# CREATE STORAGE NAME
# =========================================================

def create_storage_name(
    original_filename: str,
) -> str:

    path = Path(
        original_filename
    )

    stem = path.stem
    extension = path.suffix.lower()

    unique_id = uuid.uuid4().hex

    return (
        f"{unique_id}_{stem}{extension}"
    )


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):

    # =====================================================
    # VALIDATE FILENAME
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    # -----------------------------------------------------
    # Keep only the actual filename
    # -----------------------------------------------------

    original_filename = Path(
        file.filename
    ).name

    # =====================================================
    # VALIDATE PDF
    # =====================================================

    if (
        Path(original_filename)
        .suffix
        .lower()
        != ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # =====================================================
    # CREATE UNIQUE STORAGE NAME
    # =====================================================

    storage_name = create_storage_name(
        original_filename
    )

    file_path = (
        UPLOAD_DIR / storage_name
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n================ DOCUMENT UPLOAD ================"
    )

    print(
        "Original filename:",
        original_filename,
    )

    print(
        "Storage filename:",
        storage_name,
    )

    print(
        "Physical path:",
        file_path,
    )

    # =====================================================
    # SAVE + INDEX
    # =====================================================

    try:

        # -------------------------------------------------
        # SAVE FILE
        # -------------------------------------------------

        with open(
            file_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        print(
            "Saved file:",
            file_path,
        )

        # -------------------------------------------------
        # INDEX PDF
        #
        # VERY IMPORTANT:
        #
        # physical filename:
        # UUID_original.pdf
        #
        # Pinecone source:
        # original.pdf
        #
        # This keeps selected_document matching
        # Pinecone metadata.
        # -------------------------------------------------

        result = index_pdf(
            file_path=str(
                file_path
            ),
            document_name=original_filename,
        )

        print(
            "Indexed document:",
            original_filename,
        )

        print(
            "Pages:",
            result.get(
                "pages",
                0,
            ),
        )

        print(
            "Chunks:",
            result.get(
                "chunks",
                0,
            ),
        )

        print(
            "=================================================\n"
        )

        # =================================================
        # RESPONSE
        # =================================================

        return {
            "status": "success",

            # Name shown to frontend
            "filename": original_filename,

            # Actual physical filename
            "stored_as": storage_name,

            # Pinecone metadata source
            "display_name": original_filename,

            "pages": result.get(
                "pages",
                0,
            ),

            "chunks": result.get(
                "chunks",
                0,
            ),
        }

    except Exception as error:

        print(
            "\n================ DOCUMENT UPLOAD ERROR ================"
        )

        print(
            repr(error)
        )

        print(
            "========================================================\n"
        )

        # -------------------------------------------------
        # Delete partially saved file
        # -------------------------------------------------

        if file_path.exists():

            try:

                file_path.unlink()

            except Exception as cleanup_error:

                print(
                    "Cleanup error:",
                    repr(cleanup_error),
                )

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

    # -----------------------------------------------------
    # Read physical PDFs
    # -----------------------------------------------------

    for file in sorted(
        UPLOAD_DIR.glob("*.pdf")
    ):

        filename = file.name

        display_name = filename

        # =================================================
        # REMOVE UUID PREFIX
        #
        # Example:
        #
        # 56d39032d0cf4226a28727aaff9a9c8d_file.pdf
        #
        # becomes:
        #
        # file.pdf
        # =================================================

        if "_" in filename:

            prefix, remaining = (
                filename.split(
                    "_",
                    1,
                )
            )

            if (
                len(prefix) == 32
                and all(
                    character
                    in "0123456789abcdefABCDEF"
                    for character in prefix
                )
            ):

                display_name = remaining

        # =================================================
        # DOCUMENT INFO
        # =================================================

        documents.append(
            {
                # Physical filename
                "filename": filename,

                # User-facing filename
                "display_name": display_name,

                # File size
                "size_kb": round(
                    file.stat().st_size / 1024,
                    2,
                ),
            }
        )

    return {
        "documents": documents,
    }


# =========================================================
# VIEW PDF
# =========================================================

@router.get(
    "/view/{filename}"
)
def view_document(
    filename: str,
):

    # -----------------------------------------------------
    # Prevent path traversal
    # -----------------------------------------------------

    safe_filename = Path(
        filename
    ).name

    file_path = (
        UPLOAD_DIR /
        safe_filename
    )

    # =====================================================
    # CHECK FILE
    # =====================================================

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # =====================================================
    # RETURN PDF
    # =====================================================

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",
        },
    )