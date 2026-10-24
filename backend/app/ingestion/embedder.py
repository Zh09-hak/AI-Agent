from fastembed import TextEmbedding

class Embedder:
    def __init__(self):
        self.model_name = "BAAI/bge-small-en-v1.5"
        self.embedding_dimension = 384
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = TextEmbedding(
                model_name=self.model_name
            )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        self._load_model()
        embeddings = self.model.embed(texts)

        return [embedding.tolist() for embedding in embeddings]

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


embedder = Embedder()
