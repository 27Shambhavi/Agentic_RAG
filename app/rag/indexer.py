import uuid

from app.rag.loaders import load_pdf
from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_model
from app.rag.pinecone_client import pinecone_client


def index_pdf(file_path: str):

    pages = load_pdf(file_path)

    if not pages:
        raise ValueError(
            "No text could be extracted from this PDF."
        )

    chunks = chunk_text(pages)

    if not chunks:
        raise ValueError(
            "No chunks were generated from the PDF."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.embed_documents(
        texts
    )

    vectors = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        vector_id = str(uuid.uuid4())

        vectors.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                }
            }
        )

    pinecone_client.upsert(vectors)

    return {
        "source": file_path,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "indexed"
    }