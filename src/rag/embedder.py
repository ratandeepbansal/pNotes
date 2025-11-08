"""Generate embeddings for text using sentence transformers."""
from typing import List, Union
from sentence_transformers import SentenceTransformer

from ..utils.config import EMBEDDING_MODEL


class Embedder:
    """Handles text embedding generation."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model."""
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        This is an alias for embed_text but can be extended
        to use different encoding for queries vs documents.

        Args:
            query: The search query

        Returns:
            List of floats representing the query embedding
        """
        return self.embed_text(query)
