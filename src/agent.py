"""Instagram Coach Agent - Main agent interface."""

from typing import List, Dict, Any
from pathlib import Path

from rag_pipeline import get_rag_pipeline
from agent_modes import AgentMode, generate_with_mode, list_modes, get_mode_description


class InstagramCoachAgent:
    """
    Main agent for Instagram coaching.

    Provides a simple interface to interact with the RAG pipeline
    and get coaching insights.
    """

    def __init__(self, auto_load_data: bool = True):
        """
        Initialize the Instagram Coach Agent.

        Args:
            auto_load_data: Automatically load data from default paths.
        """
        print("\n" + "=" * 60)
        print("📸  INSTAGRAM COACH AGENT  📸")
        print("=" * 60)

        self.rag_pipeline = get_rag_pipeline()
        self.conversation_history: List[Dict[str, str]] = []
        self.current_mode: AgentMode = AgentMode.CONTENT_ANALYST  # Mode par défaut

        if auto_load_data:
            try:
                self.rag_pipeline.load_data()
                self._print_stats()
            except FileNotFoundError as e:
                print(f"\n⚠️  Warning: Could not load data automatically: {e}")
                print("   Use agent.load_data() to load data manually.\n")

    def load_data(
        self,
        posts_path: Path = None,
        profile_path: Path = None,
        force_reload: bool = False,
    ):
        """
        Load Instagram data.

        Args:
            posts_path: Path to posts JSON file.
            profile_path: Path to profile JSON file.
            force_reload: Force reload even if data exists.
        """
        self.rag_pipeline.load_data(posts_path, profile_path, force_reload)
        self._print_stats()

    def set_mode(self, mode: AgentMode):
        """
        Change le mode de l'agent.

        Args:
            mode: Nouveau mode à utiliser
        """
        self.current_mode = mode
        print(f"\n🔄 Mode changé: {get_mode_description(mode)}\n")

    def list_available_modes(self):
        """Liste tous les modes disponibles"""
        print("\n📋 Modes disponibles:\n")
        for mode_info in list_modes():
            current = (
                " (ACTUEL)" if mode_info["mode"] == self.current_mode.value else ""
            )
            print(f"  • {mode_info['description']}{current}")
        print()

    def ask(
        self,
        question: str,
        n_posts: int = 3,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        verbose: bool = False,
        stream: bool = True,
        mode: AgentMode = None,
    ) -> str:
        """
        Ask a question to the coach agent.

        Args:
            question: Your question about Instagram performance.
            n_posts: Number of relevant posts to retrieve (default: 3 for faster performance).
            temperature: LLM temperature (creativity).
            max_tokens: Maximum response length.
            verbose: Print additional information.
            stream: Stream the response for better perceived performance (default: True).
            mode: Mode d'agent à utiliser (si None, utilise self.current_mode).

        Returns:
            Agent's response.
        """
        # Utiliser le mode spécifié ou le mode actuel
        active_mode = mode or self.current_mode

        print(f"\n💬 Question: {question}")
        print(f"🤖 Mode: {get_mode_description(active_mode)}\n")

        if verbose:
            print(f"   Retrieving {n_posts} relevant posts...")

        # Generate response using the selected mode
        result = generate_with_mode(
            rag_pipeline=self.rag_pipeline,
            question=question,
            mode=active_mode,
            n_results=n_posts,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

        relevant_posts = result["relevant_posts"]

        if verbose:
            print(f"   ✓ Retrieved {len(relevant_posts)} posts")
            print("   📝 Relevant posts:")
            for i, post in enumerate(relevant_posts[:3], 1):
                metadata = post.get("metadata", {})
                caption = metadata.get("caption", "N/A")[:50]
                engagement = metadata.get("metrics", {}).get("engagement_rate", 0)
                print(f"      {i}. {caption}... (engagement: {engagement}%)")
            print()

        print("🤖 Réponse:\n")

        # Handle streaming vs non-streaming
        if stream and "response_stream" in result:
            response = ""
            try:
                for chunk in result["response_stream"]:
                    print(chunk, end="", flush=True)
                    response += chunk
            except Exception as e:
                print(f"\n\n⚠️ Streaming error: {e}", flush=True)
                import traceback

                traceback.print_exc()
            print()  # New line after streaming
        else:
            response = result["response"]
            print(response)

        print("\n" + "-" * 60 + "\n")

        # Store in conversation history
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def get_top_posts(
        self, n: int = 3, metric: str = "engagement_rate"
    ) -> List[Dict[str, Any]]:
        """
        Get top performing posts (requires all posts to be loaded).

        Args:
            n: Number of top posts to return (default: 3 for faster retrieval).
            metric: Metric to sort by.

        Returns:
            List of top posts.
        """
        # This is a simplified version - in production you'd query the vector store
        # For now, we'll use a simple retrieval
        question = f"Quels sont mes {n} meilleurs posts ?"
        result = self.rag_pipeline.generate_response(
            question, n_results=n, stream=False
        )
        return result["relevant_posts"]

    def analyze_content_type(self, content_type: str = None) -> str:
        """
        Analyze performance by content type.

        Args:
            content_type: Type to analyze (reel, photo, carousel) or None for all.

        Returns:
            Analysis response.
        """
        if content_type:
            question = f"Comment performent mes {content_type}s ?"
        else:
            question = "Quel type de contenu performe le mieux ?"

        return self.ask(question)

    def get_recommendations(self, focus: str = "general") -> str:
        """
        Get personalized recommendations.

        Args:
            focus: Focus area (general, content, growth, engagement).

        Returns:
            Recommendations response.
        """
        questions = {
            "general": "Quelles sont tes recommandations principales pour améliorer mon Instagram ?",
            "content": "Comment puis-je optimiser mon contenu ?",
            "growth": "Quelles stratégies pour accélérer ma croissance ?",
            "engagement": "Comment augmenter mon taux d'engagement ?",
        }

        question = questions.get(focus, questions["general"])
        return self.ask(question)

    def compare_periods(self) -> str:
        """
        Compare recent vs older posts performance.

        Returns:
            Comparison analysis.
        """
        question = "Compare les performances de mes posts récents vs mes anciens posts. Y a-t-il une tendance ?"
        return self.ask(question)

    def suggest_hashtags(self) -> str:
        """
        Get hashtag suggestions based on successful posts.

        Returns:
            Hashtag recommendations.
        """
        question = "Quels hashtags devrais-je utiliser basé sur mes posts qui ont le mieux performé ?"
        return self.ask(question)

    def get_posting_schedule(self) -> str:
        """
        Get recommendations for posting schedule.

        Returns:
            Posting schedule recommendations.
        """
        question = "À quelle fréquence et quand devrais-je publier pour maximiser mon engagement ?"
        return self.ask(question)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Statistics dictionary.
        """
        return self.rag_pipeline.get_statistics()

    def _print_stats(self):
        """Print agent statistics."""
        stats = self.get_stats()
        profile = stats.get("profile", {})

        print("\n" + "=" * 60)
        print(f"📊 @{profile.get('username', 'N/A')} - Statistics")
        print("=" * 60)
        print(f"  Followers: {profile.get('followers', 'N/A'):,}")
        print(f"  Avg Engagement: {profile.get('avg_engagement_rate', 'N/A')}%")
        print(f"  Niche: {profile.get('niche', 'N/A').capitalize()}")
        print(f"  Posts Indexed: {stats.get('total_posts', 0)}")
        print("=" * 60 + "\n")

    def chat(self):
        """
        Start an interactive chat session.

        Type 'quit', 'exit', or 'q' to exit.
        """
        print("\n💬 Chat mode activated!")
        print("   Type your questions or commands.")
        print("   Commands: quit, exit, q, stats, clear, modes, mode <name>")
        print("=" * 60 + "\n")

        # Afficher le mode actuel
        print(f"🤖 Mode actuel: {get_mode_description(self.current_mode)}")
        print("   Tapez 'modes' pour voir tous les modes disponibles\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Au revoir!\n")
                    break

                # Check for special commands
                if user_input.lower() == "stats":
                    self._print_stats()
                    continue

                if user_input.lower() == "clear":
                    self.conversation_history = []
                    print("\n🗑️  Conversation history cleared.\n")
                    continue

                if user_input.lower() == "modes":
                    self.list_available_modes()
                    continue

                # Commande pour changer de mode
                if user_input.lower().startswith("mode "):
                    mode_name = user_input[5:].strip().lower()
                    mode_mapping = {
                        "content": AgentMode.CONTENT_ANALYST,
                        "analyst": AgentMode.CONTENT_ANALYST,
                        "analysis": AgentMode.CONTENT_ANALYST,
                        "monetization": AgentMode.MONETIZATION,
                        "money": AgentMode.MONETIZATION,
                        "strategy": AgentMode.STRATEGY,
                        "planning": AgentMode.STRATEGY,
                        "audience": AgentMode.AUDIENCE,
                        "community": AgentMode.AUDIENCE,
                    }
                    if mode_name in mode_mapping:
                        self.set_mode(mode_mapping[mode_name])
                    else:
                        print(f"\n❌ Mode inconnu: {mode_name}")
                        print(
                            "   Modes disponibles: content, monetization, strategy, audience\n"
                        )
                    continue

                # Ask the question
                self.ask(user_input, verbose=False)

            except KeyboardInterrupt:
                print("\n\n👋 Au revoir!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point for the agent."""
    agent = InstagramCoachAgent()

    # Example usage
    print("\n🚀 Agent ready! Try these example questions:\n")
    examples = [
        "Quels sont mes posts les plus performants ?",
        "Comment améliorer mon taux d'engagement ?",
        "Quel type de contenu fonctionne le mieux ?",
        "Quelles stratégies pour augmenter mes followers ?",
    ]

    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

    print("\n💡 Or start chatting with: agent.chat()\n")

    return agent


if __name__ == "__main__":
    agent = main()
