"""
Modes d'agents pour différents types de conseils.
Permet de choisir quel type de conseiller utiliser.
"""

from typing import Dict, Any, List
from enum import Enum

from rag_pipeline import RAGPipeline
from utils.prompt_manager import PromptType, get_prompt_manager


class AgentMode(Enum):
    """Modes disponibles pour l'agent"""

    CONTENT_ANALYST = "content_analyst"  # Analyse de performance
    MONETIZATION = "monetization"  # Conseils monétisation
    STRATEGY = "strategy"  # Stratégie de contenu
    AUDIENCE = "audience"  # Analyse d'audience
    VOICE_IMPACT = "voice_impact"  # Résumé vocal de l'impact


def get_prompt_for_mode(mode: AgentMode) -> PromptType:
    """
    Retourne le type de prompt correspondant au mode.

    Args:
        mode: Mode de l'agent

    Returns:
        Type de prompt correspondant
    """
    mapping = {
        AgentMode.CONTENT_ANALYST: PromptType.CONTENT_ANALYST,
        AgentMode.MONETIZATION: PromptType.MONETIZATION_ADVISOR,
        AgentMode.STRATEGY: PromptType.CONTENT_STRATEGY,
        AgentMode.AUDIENCE: PromptType.AUDIENCE_INSIGHTS,
        AgentMode.VOICE_IMPACT: PromptType.VOICE_IMPACT_SUMMARY,
    }
    return mapping[mode]


def get_mode_description(mode: AgentMode) -> str:
    """Retourne la description d'un mode"""
    descriptions = {
        AgentMode.CONTENT_ANALYST: "📊 Analyse de Performance - Évalue vos posts et identifie ce qui fonctionne",
        AgentMode.MONETIZATION: "💰 Monétisation - Conseils sur les partenariats et revenus",
        AgentMode.STRATEGY: "🎯 Stratégie de Contenu - Planning et idées de création",
        AgentMode.AUDIENCE: "👥 Analyse d'Audience - Comprend votre communauté",
        AgentMode.VOICE_IMPACT: "🎙️ Résumé Vocal - Génère un résumé audio de l'impact de votre dernier post",
    }
    return descriptions.get(mode, "Mode inconnu")


def generate_with_mode(
    rag_pipeline: RAGPipeline,
    question: str,
    mode: AgentMode = AgentMode.CONTENT_ANALYST,
    n_results: int = 3,
    temperature: float = 0.5,
    max_tokens: int = 1000,
    stream: bool = True,
) -> Dict[str, Any]:
    """
    Génère une réponse en utilisant un mode spécifique.

    Args:
        rag_pipeline: Pipeline RAG à utiliser
        question: Question de l'utilisateur
        mode: Mode d'agent à utiliser
        n_results: Nombre de posts à récupérer
        temperature: Température du LLM
        max_tokens: Tokens maximum
        stream: Activer le streaming

    Returns:
        Dictionnaire avec la réponse et métadonnées
    """
    prompt_manager = get_prompt_manager()

    # Récupérer les posts pertinents
    relevant_posts = rag_pipeline.retrieve_relevant_posts(question, n_results)

    # Construire le contexte
    profile = rag_pipeline.influencer_profile or {}
    context = {
        "user_data": {
            "username": profile.get("username", "N/A"),
            "followers": profile.get("followers", 0),
            "engagement_rate": profile.get("avg_engagement_rate", 0),
            "niche": profile.get("niche", "N/A"),
        },
        "posts_data": relevant_posts,
        "question": question,
    }

    # Charger le prompt du mode choisi
    prompt_type = get_prompt_for_mode(mode)
    system_prompt = prompt_manager.format_prompt_with_context(prompt_type, context)

    # Construire le prompt utilisateur
    user_prompt = rag_pipeline.build_user_prompt(question, relevant_posts)

    # Générer la réponse
    if stream:
        return {
            "mode": mode.value,
            "mode_description": get_mode_description(mode),
            "response_stream": rag_pipeline.llm_client.generate_response_stream(
                user_message=user_prompt,
                system_message=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            "relevant_posts": relevant_posts,
            "question": question,
        }
    else:
        response = rag_pipeline.llm_client.generate_response(
            user_message=user_prompt,
            system_message=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "mode": mode.value,
            "mode_description": get_mode_description(mode),
            "response": response,
            "relevant_posts": relevant_posts,
            "question": question,
        }


def list_modes() -> List[Dict[str, str]]:
    """
    Liste tous les modes disponibles.

    Returns:
        Liste des modes avec descriptions
    """
    return [
        {
            "mode": mode.value,
            "description": get_mode_description(mode),
        }
        for mode in AgentMode
    ]


if __name__ == "__main__":
    # Test
    print("=== Modes disponibles ===\n")
    for mode_info in list_modes():
        print(f"{mode_info['description']}")
        print(f"  Code: {mode_info['mode']}\n")
