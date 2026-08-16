from pathlib import Path

import pymupdf


# =========================================================
# PDF LOADER
# =========================================================
#
# Supports:
#
# 1. Normal text-based PDFs
#       PyMuPDF text extraction
#
# 2. Scanned/image PDFs
#       OCR fallback
#
# Output format remains:
#
# [
#     {
#         "text": "...",
#         "page": 1,
#         "source": "file.pdf"
#     }
# ]
#
# This keeps indexer.py unchanged.
# =========================================================


def load_pdf(
    file_path: str,
) -> list[dict]:

    path = Path(
        file_path
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":

        raise ValueError(
            "Only PDF files are supported."
        )

    # =====================================================
    # OPEN PDF
    # =====================================================

    document = pymupdf.open(
        file_path
    )

    pages = []

    try:

        # =================================================
        # FIRST PASS
        #
        # Try normal PDF text extraction.
        # =================================================

        for page_number, page in enumerate(
            document
        ):

            text = (
                page.get_text(
                    "text"
                )
                or ""
            ).strip()

            if not text:

                continue

            pages.append(
                {
                    "text": text,

                    "page": (
                        page_number + 1
                    ),

                    "source": path.name,
                }
            )

    finally:

        document.close()

    # =====================================================
    # NORMAL TEXT PDF
    # =====================================================
    #
    # If text was successfully extracted,
    # return immediately.
    #
    # No OCR dependency is required.
    # =====================================================

    if pages:

        print(
            "\n================ PDF LOADER ================"
        )

        print(
            "Mode: PyMuPDF text extraction"
        )

        print(
            "File:",
            path.name,
        )

        print(
            "Pages with text:",
            len(pages),
        )

        print(
            "============================================\n"
        )

        return pages

    # =====================================================
    # OCR FALLBACK
    # =====================================================
    #
    # Re-open the document because the first document
    # has already been closed.
    # =====================================================

    print(
        "\n================ PDF LOADER ================"
    )

    print(
        "PyMuPDF found no text."
    )

    print(
        "Possible scanned/image PDF."
    )

    print(
        "Trying OCR fallback..."
    )

    print(
        "============================================\n"
    )

    try:

        return load_pdf_with_ocr(
            file_path=file_path
        )

    except ImportError as error:

        print(
            "\n[PDF OCR ERROR]"
        )

        print(
            repr(error)
        )

        raise ValueError(
            "This PDF appears to be scanned/image-based "
            "and contains no extractable text. "
            "OCR support is not installed."
        ) from error

    except Exception as error:

        print(
            "\n[PDF OCR ERROR]"
        )

        print(
            repr(error)
        )

        raise ValueError(
            "The PDF contains no directly extractable text "
            "and OCR processing failed."
        ) from error


# =========================================================
# OCR LOADER
# =========================================================
#
# Uses PyMuPDF to render each page as an image and
# pytesseract to extract text.
#
# Required:
#
# pip install pytesseract pillow
#
# AND
#
# Tesseract OCR must be installed on Windows.
#
# =========================================================


def load_pdf_with_ocr(
    file_path: str,
) -> list[dict]:

    import io

    import pytesseract

    from PIL import Image

    path = Path(
        file_path
    )

    document = pymupdf.open(
        file_path
    )

    pages = []

    try:

        for page_number, page in enumerate(
            document
        ):

            # =============================================
            # RENDER PDF PAGE
            # =============================================

            matrix = pymupdf.Matrix(
                2,
                2,
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

            # =============================================
            # OCR
            # =============================================

            text = pytesseract.image_to_string(
                image
            )

            text = (
                text or ""
            ).strip()

            if not text:

                print(
                    f"[OCR] Page {page_number + 1}: "
                    "no text detected"
                )

                continue

            pages.append(
                {
                    "text": text,

                    "page": (
                        page_number + 1
                    ),

                    "source": path.name,
                }
            )

            print(
                f"[OCR] Page {page_number + 1}: "
                f"{len(text)} characters"
            )

    finally:

        document.close()

    # =====================================================
    # OCR RESULT
    # =====================================================

    if not pages:

        raise ValueError(
            "No text could be extracted from this PDF "
            "using either PyMuPDF or OCR."
        )

    print(
        "\n================ PDF OCR ================"
    )

    print(
        "File:",
        path.name,
    )

    print(
        "OCR pages:",
        len(pages),
    )

    print(
        "=========================================\n"
    )

    return pages