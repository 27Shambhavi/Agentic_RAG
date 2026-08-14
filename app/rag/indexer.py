from pathlib import Path
import uuid

from app.rag.loaders import load_pdf
from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


# =========================================================
# INDEX PDF
# =========================================================

def index_pdf(
    file_path: str,
    document_name: str | None = None,
):

    file_path = str(file_path)

    # -----------------------------------------------------
    # DISPLAY / METADATA NAME
    #
    # IMPORTANT:
    # document_name = original filename shown in UI
    # file_path      = actual UUID storage path
    # -----------------------------------------------------

    source_name = (
        document_name
        if document_name
        else Path(file_path).name
    )

    print("\n================ INDEX PDF ================")
    print("Physical file :", file_path)
    print("Document name :", source_name)

    # -----------------------------------------------------
    # LOAD PDF
    # -----------------------------------------------------

    pages = load_pdf(
        file_path
    )

    if not pages:

        raise ValueError(
            "No text could be extracted from this PDF."
        )

    print(
        "Pages:",
        len(pages)
    )

    # -----------------------------------------------------
    # CHUNK
    # -----------------------------------------------------

    chunks = chunk_text(
        pages
    )

    if not chunks:

        raise ValueError(
            "No chunks were generated from this PDF."
        )

    print(
        "Chunks:",
        len(chunks)
    )

    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = (
        embedding_model.embed_documents(
            texts
        )
    )

    # -----------------------------------------------------
    # BUILD VECTORS
    # -----------------------------------------------------

    vectors = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):

        vector_id = str(
            uuid.uuid4()
        )

        vectors.append(
            {
                "id": vector_id,

                "values": embedding,

                "metadata": {
                    # IMPORTANT:
                    # Always store ORIGINAL filename
                    # so frontend selected_document
                    # matches Pinecone filter.
                    "source": source_name,

                    "page": chunk.get(
                        "page",
                        "",
                    ),

                    "text": chunk.get(
                        "text",
                        "",
                    ),
                },
            }
        )

    # -----------------------------------------------------
    # UPSERT
    # -----------------------------------------------------

    pinecone_client.upsert(
        vectors
    )

    print(
        "Vectors indexed:",
        len(vectors)
    )

    print(
        "==========================================\n"
    )

    return {
        "source": source_name,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "indexed",
    }