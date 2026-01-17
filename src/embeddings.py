"""Embedding generation using sentence-transformers."""

from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

from config import config


class EmbeddingGenerator:
    """Generate text embeddings using sentence-transformers."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Defaults to config value.
        """
        self.model_name = model_name or config.embedding.model_name
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"✓ Model loaded successfully (dimension: {config.embedding.dimension})")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as numpy array.
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed.

        Returns:
            Array of embedding vectors.
        """
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    def create_post_text(self, post: dict) -> str:
        """
        Create enriched text representation of an Instagram post.

        Args:
            post: Instagram post dictionary.

        Returns:
            Formatted text combining caption and metadata.
        """
        metrics = post.get("metrics", {})

        text = f"""Caption: {post.get("caption", "")}
Type de contenu: {post.get("media_type", "unknown")}
Date: {post.get("timestamp", "")}
Taux d'engagement: {metrics.get("engagement_rate", 0)}%
Likes: {metrics.get("likes", 0)}
Commentaires: {metrics.get("comments", 0)}
Partages: {metrics.get("shares", 0)}
Sauvegardes: {metrics.get("saves", 0)}
Portée: {metrics.get("reach", 0)}
Impressions: {metrics.get("impressions", 0)}
Hashtags: {", ".join(post.get("hashtags", []))}"""

        return text

    def embed_post(self, post: dict) -> tuple[np.ndarray, str]:
        """
        Generate embedding for an Instagram post.

        Args:
            post: Instagram post dictionary.

        Returns:
            Tuple of (embedding vector, formatted text).
        """
        text = self.create_post_text(post)
        embedding = self.embed_text(text)
        return embedding, text


# Global instance
_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create global embedding generator instance."""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
