from app.rag.pinecone_client import pinecone_client


if __name__ == "__main__":

    print("Pinecone index is ready.")

    print(
        f"Index: {pinecone_client.index_name}"
    )