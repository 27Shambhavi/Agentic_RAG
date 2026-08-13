from sentence_transformers import SentenceTransformer

from app.config.settings import settings


class EmbeddingModel:

    def __init__(self):

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

    def embed_text(
        self,
        text: str
    ) -> list[float]:

        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return vectors.tolist()


embedding_model = EmbeddingModel()