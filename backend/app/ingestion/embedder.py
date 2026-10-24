from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model_name = model_name
        self.model = None
        self.embedding_dimension = 384

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(
                self.model_name,
                device="cpu",
            )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


embedder = Embedder()
