"""Vector store management using ChromaDB."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import json

from config import config


class VectorStore:
    """Manage Instagram posts in ChromaDB vector store."""

    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_directory: Directory to persist the database.
            collection_name: Name of the collection.
        """
        self.persist_directory = (
            persist_directory or config.vector_store.persist_directory
        )
        self.collection_name = collection_name or config.vector_store.collection_name

        print(f"Initializing ChromaDB at: {self.persist_directory}")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Instagram posts with embeddings"},
        )

        print(f"✓ ChromaDB initialized (collection: {self.collection_name})")
        print(f"  Current document count: {self.collection.count()}")

    def add_post(
        self, post_id: str, embedding: List[float], text: str, metadata: Dict[str, Any]
    ):
        """
        Add a single post to the vector store.

        Args:
            post_id: Unique ID of the post.
            embedding: Embedding vector.
            text: Original text of the post.
            metadata: Post metadata (metrics, etc.).
        """
        # ChromaDB doesn't support nested dicts in metadata, so we flatten it
        flat_metadata = self._flatten_metadata(metadata)

        self.collection.add(
            ids=[post_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[flat_metadata],
        )

    def add_posts(
        self,
        post_ids: List[str],
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: List[Dict[str, Any]],
    ):
        """
        Add multiple posts to the vector store.

        Args:
            post_ids: List of unique post IDs.
            embeddings: List of embedding vectors.
            texts: List of post texts.
            metadatas: List of post metadata dicts.
        """
        flat_metadatas = [self._flatten_metadata(m) for m in metadatas]

        self.collection.add(
            ids=post_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=flat_metadatas,
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar posts.

        Args:
            query_embedding: Query embedding vector.
            n_results: Number of results to return.
            where: Optional metadata filter.

        Returns:
            List of matching posts with metadata and distances.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results, where=where
        )

        # Format results
        formatted_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, post_id in enumerate(results["ids"][0]):
                formatted_results.append(
                    {
                        "id": post_id,
                        "distance": results["distances"][0][i]
                        if "distances" in results
                        else None,
                        "text": results["documents"][0][i]
                        if "documents" in results
                        else None,
                        "metadata": self._unflatten_metadata(results["metadatas"][0][i])
                        if "metadatas" in results
                        else {},
                    }
                )

        return formatted_results

    def get_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a post by its ID.

        Args:
            post_id: Post ID to retrieve.

        Returns:
            Post data or None if not found.
        """
        try:
            result = self.collection.get(ids=[post_id])
            if result and result["ids"]:
                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0] if "documents" in result else None,
                    "metadata": self._unflatten_metadata(result["metadatas"][0])
                    if "metadatas" in result
                    else {},
                }
        except Exception as e:
            print(f"Error getting post {post_id}: {e}")
        return None

    def delete_all(self):
        """Delete all posts from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Instagram posts with embeddings"},
        )
        print(f"✓ Collection '{self.collection_name}' reset")

    def count(self) -> int:
        """Get the number of posts in the collection."""
        return self.collection.count()

    def get_all(self) -> Dict[str, Any]:
        """
        Récupère tous les posts de la collection.

        Returns:
            Dictionnaire avec ids, documents et metadatas
        """
        try:
            result = self.collection.get()
            if result and result["ids"]:
                # Unflatten les métadonnées
                unflattened_metadatas = [
                    self._unflatten_metadata(m) for m in result.get("metadatas", [])
                ]
                return {
                    "ids": result["ids"],
                    "documents": result.get("documents", []),
                    "metadatas": unflattened_metadatas,
                }
        except Exception as e:
            print(f"Error getting all posts: {e}")

        return {"ids": [], "documents": [], "metadatas": []}

    def _flatten_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested metadata for ChromaDB compatibility.

        ChromaDB requires flat dictionaries for metadata.
        """
        flat = {}

        for key, value in metadata.items():
            if key == "metrics" and isinstance(value, dict):
                # Flatten metrics
                for metric_key, metric_value in value.items():
                    flat[f"metrics_{metric_key}"] = metric_value
            elif key == "hashtags" and isinstance(value, list):
                # Convert list to comma-separated string
                flat["hashtags"] = ",".join(value)
            elif isinstance(value, (str, int, float, bool)):
                flat[key] = value
            else:
                # Convert other types to JSON string
                flat[key] = json.dumps(value)

        return flat

    def _unflatten_metadata(self, flat_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unflatten metadata back to original structure.
        """
        metadata = {}
        metrics = {}

        for key, value in flat_metadata.items():
            if key.startswith("metrics_"):
                # Restore metrics
                metric_key = key.replace("metrics_", "")
                metrics[metric_key] = value
            elif key == "hashtags" and isinstance(value, str):
                # Restore hashtags list
                metadata["hashtags"] = value.split(",") if value else []
            else:
                metadata[key] = value

        if metrics:
            metadata["metrics"] = metrics

        return metadata


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
