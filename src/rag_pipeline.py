"""RAG (Retrieval-Augmented Generation) pipeline for Instagram coach."""

import json
from typing import List, Dict, Any
from pathlib import Path

from config import config
from embeddings import get_embedding_generator
from vector_store import get_vector_store
from llm_client import get_llm_client


class RAGPipeline:
    """Complete RAG pipeline for Instagram coaching."""

    def __init__(self):
        """Initialize the RAG pipeline components."""
        print("\n=== Initializing RAG Pipeline ===")

        self.embedding_gen = get_embedding_generator()
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()

        self.influencer_profile = None

        print("✓ RAG Pipeline initialized\n")

    def load_data(
        self,
        posts_path: Path = None,
        profile_path: Path = None,
        force_reload: bool = False,
    ):
        """
        Load Instagram data from JSON files.

        Args:
            posts_path: Path to posts JSON file.
            profile_path: Path to profile JSON file.
            force_reload: Force reload even if data exists in vector store.
        """
        posts_path = posts_path or config.posts_data_path
        profile_path = profile_path or config.profile_data_path

        print("\n=== Loading Data ===")
        print(f"Posts: {posts_path}")
        print(f"Profile: {profile_path}")

        # Load profile
        with open(profile_path, "r", encoding="utf-8") as f:
            self.influencer_profile = json.load(f)
            print(f"✓ Loaded profile: @{self.influencer_profile['username']}")

        # Check if we need to reload posts
        current_count = self.vector_store.count()
        if current_count > 0 and not force_reload:
            print(
                f"✓ Vector store already contains {current_count} posts (use force_reload=True to reload)"
            )
            return

        # Load posts
        with open(posts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            posts = data.get("posts", [])
            print(f"✓ Loaded {len(posts)} posts from JSON")

        # Index posts
        self.index_posts(posts)

    def index_posts(self, posts: List[Dict[str, Any]]):
        """
        Index Instagram posts into the vector store.

        Args:
            posts: List of Instagram post dictionaries.
        """
        print(f"\n=== Indexing {len(posts)} Posts ===")

        post_ids = []
        embeddings = []
        texts = []
        metadatas = []

        for i, post in enumerate(posts, 1):
            # Generate embedding and text
            embedding, text = self.embedding_gen.embed_post(post)

            post_ids.append(post["id"])
            embeddings.append(embedding.tolist())
            texts.append(text)
            metadatas.append(post)

            if i % 10 == 0:
                print(f"  Processed {i}/{len(posts)} posts...")

        # Add to vector store
        self.vector_store.add_posts(post_ids, embeddings, texts, metadatas)

        print(f"✓ Indexed {len(posts)} posts successfully")
        print(f"  Total documents in store: {self.vector_store.count()}\n")

    def retrieve_relevant_posts(
        self, question: str, n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve posts relevant to a question.

        Args:
            question: User's question.
            n_results: Number of posts to retrieve.

        Returns:
            List of relevant posts with metadata.
        """
        # Generate embedding for the question
        query_embedding = self.embedding_gen.embed_text(question)

        # Query vector store
        results = self.vector_store.query(
            query_embedding=query_embedding.tolist(), n_results=n_results
        )

        return results

    def format_posts_for_prompt(self, posts: List[Dict[str, Any]]) -> str:
        """
        Format retrieved posts for inclusion in the LLM prompt.

        Args:
            posts: List of post dictionaries from retrieval.

        Returns:
            Formatted string for prompt.
        """
        if not posts:
            return "Aucun post pertinent trouvé."

        formatted = []
        for i, post in enumerate(posts, 1):
            metadata = post.get("metadata", {})
            metrics = metadata.get("metrics", {})

            post_text = f"""
POST {i}:
- Caption: {metadata.get("caption", "N/A")}
- Type: {metadata.get("media_type", "N/A")}
- Date: {metadata.get("timestamp", "N/A")}
- Engagement: {metrics.get("engagement_rate", 0)}%
- Likes: {metrics.get("likes", 0)} | Commentaires: {metrics.get("comments", 0)} | Sauvegardes: {metrics.get("saves", 0)}
- Portée: {metrics.get("reach", 0)} | Impressions: {metrics.get("impressions", 0)}
- Hashtags: {", ".join(metadata.get("hashtags", []))}
"""
            formatted.append(post_text.strip())

        return "\n\n".join(formatted)

    def build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM.

        Returns:
            System prompt string.
        """
        return """Tu es un coach Instagram expert en stratégie de contenu et analyse de données.

RÈGLES ESSENTIELLES:
- Base tes conseils UNIQUEMENT sur les données fournies (engagement, portée, impressions, sauvegardes, etc.)
- Identifie les patterns de performance dans les posts
- Compare les posts performants vs non performants avec des chiffres précis
- Adapte tes conseils au profil de l'utilisateur (niche, objectifs, taille de compte)
- Aucune recommandation générique - tout doit être justifié par les données

STRUCTURE DE RÉPONSE:

1. ANALYSE: Constats factuels avec chiffres précis

2. INSIGHTS: Ce qui fonctionne/ne fonctionne pas et pourquoi

3. RECOMMANDATIONS (3-5 max): Actions concrètes et applicables immédiatement
   - Quoi faire
   - Comment le faire
   - Pourquoi (justifié par les données)

Réponds de manière concise, personnalisée et basée sur les données."""

    def build_user_prompt(
        self, question: str, relevant_posts: List[Dict[str, Any]]
    ) -> str:
        """
        Build the user prompt with context.

        Args:
            question: User's question.
            relevant_posts: Retrieved relevant posts.

        Returns:
            Complete user prompt.
        """
        profile = self.influencer_profile or {}

        prompt = f"""PROFIL INFLUENCEUR:
- Username: @{profile.get("username", "N/A")}
- Followers: {profile.get("followers", "N/A"):,}
- Taux d'engagement moyen: {profile.get("avg_engagement_rate", "N/A")}%
- Niche: {profile.get("niche", "N/A")}
- Fréquence de publication: {profile.get("posting_frequency", "N/A")}

POSTS PERTINENTS:
{self.format_posts_for_prompt(relevant_posts)}

QUESTION:
{question}

Réponds de manière personnalisée en te basant sur les données ci-dessus."""

        return prompt

    def generate_response(
        self,
        question: str,
        n_results: int = 3,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response to a user question using RAG.

        Args:
            question: User's question.
            n_results: Number of posts to retrieve (default: 3 for faster retrieval).
            temperature: LLM temperature.
            max_tokens: Maximum tokens for response.
            stream: Whether to stream the response.

        Returns:
            Dictionary with response and metadata.
        """
        # Retrieve relevant posts
        relevant_posts = self.retrieve_relevant_posts(question, n_results)

        # Build prompts
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(question, relevant_posts)

        # Generate response
        if stream:
            # For streaming, return generator
            return {
                "response_stream": self.llm_client.generate_response_stream(
                    user_message=user_prompt,
                    system_message=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                "relevant_posts": relevant_posts,
                "question": question,
                "n_posts_retrieved": len(relevant_posts),
            }
        else:
            response = self.llm_client.generate_response(
                user_message=user_prompt,
                system_message=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return {
                "response": response,
                "relevant_posts": relevant_posts,
                "question": question,
                "n_posts_retrieved": len(relevant_posts),
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics from the indexed posts.

        Returns:
            Dictionary of statistics.
        """
        if not self.influencer_profile:
            return {}

        return {
            "profile": self.influencer_profile,
            "total_posts": self.vector_store.count(),
        }


# Global instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create global RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
