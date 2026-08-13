import sys

from app.rag.indexer import index_pdf


def main():

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            'python -m scripts.ingest_documents '
            '"data/documents/file.pdf"'
        )

        sys.exit(1)

    pdf_path = sys.argv[1]

    try:

        result = index_pdf(pdf_path)

        print("\nDocument indexing complete.")
        print("-" * 50)

        print(
            f"Source : {result['source']}"
        )

        print(
            f"Pages  : {result['pages']}"
        )

        print(
            f"Chunks : {result['chunks']}"
        )

        print(
            f"Status : {result['status']}"
        )

    except Exception as error:

        print("\nDocument indexing failed.")
        print("-" * 50)
        print(error)

        sys.exit(1)


if __name__ == "__main__":
    main()