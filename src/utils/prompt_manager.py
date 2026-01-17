"""
Module de gestion des prompts système pour les différents agents IA.
Permet de charger et gérer les prompts spécialisés pour chaque type d'analyse.
"""

from pathlib import Path
from typing import Dict, Optional
from enum import Enum


class PromptType(Enum):
    """Types de prompts disponibles"""

    CONTENT_ANALYST = "content_analyst"
    MONETIZATION_ADVISOR = "monetization_advisor"
    CONTENT_STRATEGY = "content_strategy"
    AUDIENCE_INSIGHTS = "audience_insights"
    VOICE_IMPACT_SUMMARY = "voice_impact_summary"


class PromptManager:
    """Gestionnaire centralisé des prompts système"""

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialise le gestionnaire de prompts.

        Args:
            prompts_dir: Chemin vers le dossier contenant les prompts.
                        Par défaut: src/prompts/
        """
        if prompts_dir is None:
            # Déterminer le chemin du dossier prompts
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            prompts_dir = project_root / "src" / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self._prompts_cache: Dict[PromptType, str] = {}

        # Mapping des types de prompts vers les fichiers
        self._prompt_files = {
            PromptType.CONTENT_ANALYST: "content_analyst_prompt.txt",
            PromptType.MONETIZATION_ADVISOR: "monetization_advisor_prompt.txt",
            PromptType.CONTENT_STRATEGY: "content_strategy_prompt.txt",
            PromptType.AUDIENCE_INSIGHTS: "audience_insights_prompt.txt",
            PromptType.VOICE_IMPACT_SUMMARY: "voice_impact_summary_prompt.txt",
        }

    def load_prompt(self, prompt_type: PromptType, force_reload: bool = False) -> str:
        """
        Charge un prompt depuis le fichier correspondant.

        Args:
            prompt_type: Type de prompt à charger
            force_reload: Si True, recharge le prompt même s'il est en cache

        Returns:
            Le contenu du prompt

        Raises:
            FileNotFoundError: Si le fichier de prompt n'existe pas
            ValueError: Si le type de prompt est invalide
        """
        # Vérifier le cache si pas de rechargement forcé
        if not force_reload and prompt_type in self._prompts_cache:
            return self._prompts_cache[prompt_type]

        # Obtenir le nom du fichier
        if prompt_type not in self._prompt_files:
            raise ValueError(f"Type de prompt invalide: {prompt_type}")

        filename = self._prompt_files[prompt_type]
        filepath = self.prompts_dir / filename

        # Charger le contenu
        if not filepath.exists():
            raise FileNotFoundError(
                f"Fichier de prompt introuvable: {filepath}\n"
                f"Assurez-vous que le fichier existe dans {self.prompts_dir}"
            )

        with open(filepath, "r", encoding="utf-8") as f:
            prompt_content = f.read()

        # Mettre en cache
        self._prompts_cache[prompt_type] = prompt_content

        return prompt_content

    def get_all_prompts(self) -> Dict[PromptType, str]:
        """
        Charge tous les prompts disponibles.

        Returns:
            Dictionnaire avec tous les prompts chargés
        """
        prompts = {}
        for prompt_type in PromptType:
            try:
                prompts[prompt_type] = self.load_prompt(prompt_type)
            except FileNotFoundError as e:
                print(f"Attention: {e}")

        return prompts

    def reload_all_prompts(self):
        """Recharge tous les prompts depuis les fichiers"""
        self._prompts_cache.clear()
        return self.get_all_prompts()

    def format_prompt_with_context(
        self, prompt_type: PromptType, context: Dict[str, any]
    ) -> str:
        """
        Charge un prompt et ajoute du contexte spécifique.

        Args:
            prompt_type: Type de prompt à charger
            context: Dictionnaire contenant les variables de contexte
                    (ex: données utilisateur, métriques, historique)

        Returns:
            Le prompt formaté avec le contexte
        """
        base_prompt = self.load_prompt(prompt_type)

        # Construire le contexte formaté
        context_section = "\n\n# CONTEXTE ACTUEL\n\n"

        if "user_data" in context:
            context_section += "## Données du créateur\n"
            user_data = context["user_data"]
            if "username" in user_data:
                context_section += f"- Username: @{user_data['username']}\n"
            if "followers" in user_data:
                context_section += f"- Followers: {user_data['followers']:,}\n"
            if "engagement_rate" in user_data:
                context_section += (
                    f"- Taux d'engagement moyen: {user_data['engagement_rate']:.2f}%\n"
                )

        if "metrics" in context:
            context_section += "\n## Métriques récentes\n"
            metrics = context["metrics"]
            for key, value in metrics.items():
                context_section += f"- {key}: {value}\n"

        if "posts_data" in context:
            posts = context["posts_data"]
            context_section += "\n## Données de contenu\n"
            context_section += f"- Nombre de posts analysés: {len(posts)}\n"
            if posts:
                avg_likes = sum(p.get("likes", 0) for p in posts) / len(posts)
                avg_comments = sum(p.get("comments", 0) for p in posts) / len(posts)
                context_section += f"- Moyenne de likes: {avg_likes:.0f}\n"
                context_section += f"- Moyenne de commentaires: {avg_comments:.0f}\n"

        if "question" in context:
            context_section += (
                f"\n## Question de l'utilisateur\n{context['question']}\n"
            )

        return base_prompt + context_section

    def list_available_prompts(self) -> list:
        """
        Liste tous les prompts disponibles.

        Returns:
            Liste des types de prompts avec leur description
        """
        available = []
        for prompt_type in PromptType:
            filename = self._prompt_files[prompt_type]
            filepath = self.prompts_dir / filename
            exists = filepath.exists()

            available.append(
                {
                    "type": prompt_type.value,
                    "filename": filename,
                    "exists": exists,
                    "path": str(filepath),
                }
            )

        return available


# Instance globale du gestionnaire (singleton pattern)
_prompt_manager_instance = None


def get_prompt_manager() -> PromptManager:
    """
    Récupère l'instance globale du gestionnaire de prompts.
    Crée l'instance si elle n'existe pas encore.

    Returns:
        Instance du PromptManager
    """
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance


# Fonctions utilitaires pour un usage simple
def load_prompt(prompt_type: PromptType) -> str:
    """Charge un prompt via le gestionnaire global"""
    return get_prompt_manager().load_prompt(prompt_type)


def load_prompt_with_context(prompt_type: PromptType, context: Dict) -> str:
    """Charge un prompt avec contexte via le gestionnaire global"""
    return get_prompt_manager().format_prompt_with_context(prompt_type, context)


if __name__ == "__main__":
    # Test du module
    print("=== Test du PromptManager ===\n")

    manager = PromptManager()

    # Lister les prompts disponibles
    print("Prompts disponibles:")
    for prompt_info in manager.list_available_prompts():
        status = "✓" if prompt_info["exists"] else "✗"
        print(f"{status} {prompt_info['type']}: {prompt_info['filename']}")

    print("\n" + "=" * 50 + "\n")

    # Tester le chargement d'un prompt
    try:
        prompt = manager.load_prompt(PromptType.CONTENT_ANALYST)
        print(f"✓ Prompt CONTENT_ANALYST chargé ({len(prompt)} caractères)")
        print(f"Aperçu: {prompt[:200]}...\n")
    except FileNotFoundError as e:
        print(f"✗ Erreur: {e}\n")

    # Tester le formatage avec contexte
    context = {
        "user_data": {
            "username": "test_user",
            "followers": 15000,
            "engagement_rate": 4.5,
        },
        "question": "Comment améliorer mon taux d'engagement ?",
    }

    try:
        formatted = manager.format_prompt_with_context(
            PromptType.CONTENT_ANALYST, context
        )
        print(f"✓ Prompt formaté avec contexte ({len(formatted)} caractères)")
        print(f"Les 300 derniers caractères:\n...{formatted[-300:]}")
    except FileNotFoundError as e:
        print(f"✗ Erreur: {e}")
