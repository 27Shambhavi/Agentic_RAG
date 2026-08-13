from pinecone import Pinecone, ServerlessSpec

from app.config.settings import settings


class PineconeClient:

    def __init__(self):

        # =====================================================
        # VALIDATE API KEY
        # =====================================================

        if not settings.PINECONE_API_KEY:

            raise ValueError(
                "PINECONE_API_KEY not found in .env"
            )


        # =====================================================
        # CREATE CLIENT
        # =====================================================

        self.client = Pinecone(
            api_key=settings.PINECONE_API_KEY
        )


        # =====================================================
        # INDEX
        # =====================================================

        self.index_name = (
            settings.PINECONE_INDEX_NAME
        )


        self._create_index_if_needed()


        self.index = self.client.Index(
            self.index_name
        )


    # =========================================================
    # CREATE INDEX IF NEEDED
    # =========================================================

    def _create_index_if_needed(self):

        existing_indexes = (
            self.client.list_indexes()
        )


        existing_names = [
            index["name"]
            for index in existing_indexes
        ]


        if self.index_name not in existing_names:

            self.client.create_index(
                name=self.index_name,
                dimension=(
                    settings.EMBEDDING_DIMENSION
                ),
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION,
                ),
            )


    # =========================================================
    # UPSERT
    # =========================================================

    def upsert(
        self,
        vectors: list[dict],
        namespace: str = "default",
    ):

        return self.index.upsert(
            vectors=vectors,
            namespace=namespace,
        )


    # =========================================================
    # QUERY
    # =========================================================

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        namespace: str = "default",
        filter: dict | None = None,
    ):

        # -----------------------------------------------------
        # Build query arguments
        # -----------------------------------------------------

        query_kwargs = {
            "vector": vector,
            "top_k": top_k,
            "include_metadata": True,
            "namespace": namespace,
        }


        # -----------------------------------------------------
        # Add metadata filter ONLY when provided
        # -----------------------------------------------------

        if filter:

            query_kwargs["filter"] = filter


        # -----------------------------------------------------
        # Pinecone query
        # -----------------------------------------------------

        return self.index.query(
            **query_kwargs
        )


# =============================================================
# SINGLE CLIENT
# =============================================================

pinecone_client = PineconeClient()