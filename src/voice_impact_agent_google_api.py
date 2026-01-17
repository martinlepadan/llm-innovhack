"""
Agent IA vocal pour générer des résumés audio de l'impact du dernier post.
Utilise Google Cloud Text-to-Speech via API REST avec clé API.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import requests
import base64

from rag_pipeline import RAGPipeline
from utils.prompt_manager import PromptType, get_prompt_manager


class VoiceImpactAgent:
    """Agent vocal qui génère un résumé audio de l'impact du dernier post avec Google TTS API"""

    def __init__(
        self,
        rag_pipeline: RAGPipeline,
        google_api_key: str,
        voice_name: str = "fr-FR-Neural2-F",
        language_code: str = "fr-FR",
        output_dir: Optional[str] = None,
    ):
        """
        Initialise l'agent vocal avec Google Cloud TTS API.

        Args:
            rag_pipeline: Pipeline RAG pour récupérer les données
            google_api_key: Clé API Google Cloud
            voice_name: Nom de la voix Google (fr-FR-Neural2-A, fr-FR-Wavenet-A, etc.)
            language_code: Code de langue (fr-FR pour français)
            output_dir: Dossier de sortie pour les fichiers audio
        """
        self.rag_pipeline = rag_pipeline
        self.prompt_manager = get_prompt_manager()

        # Configuration Google Cloud
        self.api_key = google_api_key
        self.api_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.voice_name = voice_name
        self.language_code = language_code

        # Voix disponibles pour le français:
        # fr-FR-Neural2-F: Voix féminine Neural2 (recommandée)
        # fr-FR-Neural2-G: Voix masculine Neural2
        # fr-FR-Wavenet-F: Voix féminine haute qualité
        # fr-FR-Wavenet-G: Voix masculine haute qualité
        # fr-FR-Studio-A: Voix féminine studio
        # fr-FR-Studio-D: Voix masculine studio
        # fr-FR-Standard-F: Voix féminine standard
        # fr-FR-Standard-G: Voix masculine standard
        # fr-FR-Polyglot-1: Voix masculine polyglotte

        # Dossier de sortie
        if output_dir is None:
            self.output_dir = Path("output/voice_summaries")
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("✓ Voice Impact Agent initialisé avec Google Cloud TTS API")
        print(f"  Voix: {self.voice_name}")
        print(f"  Langue: {self.language_code}")

    def get_latest_post(self) -> Optional[Dict[str, Any]]:
        """
        Récupère le dernier post du créateur.

        Returns:
            Dictionnaire avec les données du dernier post ou None
        """
        # Récupérer tous les posts depuis le vector store
        all_results = self.rag_pipeline.vector_store.get_all()

        if not all_results or "metadatas" not in all_results:
            return None

        all_posts = all_results["metadatas"]

        if not all_posts:
            return None

        # Trier par timestamp (le plus récent en premier)
        sorted_posts = sorted(
            all_posts,
            key=lambda p: p.get("timestamp", ""),
            reverse=True,
        )

        return sorted_posts[0] if sorted_posts else None

    def calculate_impact_metrics(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les métriques d'impact du post.

        Args:
            post: Données du post

        Returns:
            Dictionnaire avec les métriques calculées
        """
        metrics = post.get("metrics", {})
        profile = self.rag_pipeline.influencer_profile or {}

        # Métriques brutes
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        saves = metrics.get("saves", 0)
        reach = metrics.get("reach", 0)
        impressions = metrics.get("impressions", 0)

        # Taux d'engagement
        engagement_rate = metrics.get("engagement_rate", 0)

        # Calculer la moyenne du compte
        all_results = self.rag_pipeline.vector_store.get_all()
        all_posts = all_results.get("metadatas", [])
        if len(all_posts) > 1:
            # Exclure le post actuel pour calculer la moyenne
            other_posts = [p for p in all_posts if p.get("id") != post.get("id")]
            avg_engagement = sum(
                p.get("metrics", {}).get("engagement_rate", 0) for p in other_posts
            ) / len(other_posts)
            avg_likes = sum(
                p.get("metrics", {}).get("likes", 0) for p in other_posts
            ) / len(other_posts)
            avg_comments = sum(
                p.get("metrics", {}).get("comments", 0) for p in other_posts
            ) / len(other_posts)
            avg_saves = sum(
                p.get("metrics", {}).get("saves", 0) for p in other_posts
            ) / len(other_posts)
        else:
            avg_engagement = engagement_rate
            avg_likes = likes
            avg_comments = comments
            avg_saves = saves

        # Comparaison avec la moyenne
        engagement_diff_pct = (
            ((engagement_rate - avg_engagement) / avg_engagement * 100)
            if avg_engagement > 0
            else 0
        )

        # Viralité (reach vs followers)
        followers = profile.get("followers", 1)
        virality_ratio = (reach / followers * 100) if followers > 0 else 0

        # Type d'engagement (actif vs passif)
        total_interactions = likes + comments + shares + saves
        active_engagement_pct = (
            ((comments + shares + saves) / total_interactions * 100)
            if total_interactions > 0
            else 0
        )

        return {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "reach": reach,
            "impressions": impressions,
            "engagement_rate": engagement_rate,
            "avg_engagement": avg_engagement,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_saves": avg_saves,
            "engagement_diff_pct": engagement_diff_pct,
            "virality_ratio": virality_ratio,
            "active_engagement_pct": active_engagement_pct,
        }

    def generate_voice_summary(
        self,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> Dict[str, Any]:
        """
        Génère un résumé vocal de l'impact du dernier post.

        Args:
            temperature: Température du LLM
            max_tokens: Tokens maximum

        Returns:
            Dictionnaire avec le texte, les métriques et le chemin audio
        """
        # Récupérer le dernier post
        latest_post = self.get_latest_post()

        if not latest_post:
            raise ValueError("Aucun post trouvé pour générer un résumé vocal")

        # Calculer les métriques d'impact
        impact_metrics = self.calculate_impact_metrics(latest_post)

        # Construire le contexte
        profile = self.rag_pipeline.influencer_profile or {}
        context = {
            "user_data": {
                "username": profile.get("username", "N/A"),
                "followers": profile.get("followers", 0),
                "engagement_rate": profile.get("avg_engagement_rate", 0),
                "niche": profile.get("niche", "N/A"),
            },
            "latest_post": {
                "id": latest_post.get("id"),
                "caption": latest_post.get("caption", ""),
                "media_type": latest_post.get("media_type", ""),
                "timestamp": latest_post.get("timestamp", ""),
                "hashtags": latest_post.get("hashtags", []),
            },
            "impact_metrics": impact_metrics,
        }

        # Charger le prompt vocal
        system_prompt = self.prompt_manager.load_prompt(PromptType.VOICE_IMPACT_SUMMARY)

        # Ajouter le contexte au prompt
        system_prompt_with_context = self._add_context_to_prompt(system_prompt, context)

        # Construire le prompt utilisateur
        user_prompt = self._build_user_prompt(latest_post, impact_metrics)

        # Générer le résumé textuel via le LLM
        summary_text = self.rag_pipeline.llm_client.generate_response(
            user_message=user_prompt,
            system_message=system_prompt_with_context,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Nettoyer le texte pour l'audio (enlever markdown, etc.)
        clean_text = self._clean_text_for_speech(summary_text)

        return {
            "text": summary_text,
            "clean_text": clean_text,
            "post_id": latest_post.get("id"),
            "metrics": impact_metrics,
            "context": context,
        }

    def generate_audio(
        self,
        text: str,
        filename: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
    ) -> str:
        """
        Convertit le texte en audio avec Google Cloud TTS API REST.

        Args:
            text: Texte à convertir en audio
            filename: Nom du fichier de sortie (auto-généré si None)
            speaking_rate: Vitesse de parole (0.25 à 4.0, 1.0 = normal)
            pitch: Hauteur de la voix (-20.0 à 20.0, 0.0 = normal)

        Returns:
            Chemin vers le fichier audio généré
        """
        # Générer le nom de fichier si non fourni
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_summary_{timestamp}.mp3"

        # Chemin complet
        output_path = self.output_dir / filename

        # Préparer la requête API
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": self.language_code,
                "name": self.voice_name,
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": speaking_rate,
                "pitch": pitch,
            },
        }

        # Faire la requête à l'API Google Cloud TTS
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            # Récupérer l'audio en base64
            result = response.json()
            audio_content = base64.b64decode(result["audioContent"])

            # Sauvegarder le fichier audio
            with open(output_path, "wb") as out:
                out.write(audio_content)

            print(f"✓ Audio généré: {output_path}")

            return str(output_path)

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.text if e.response else str(e)
            raise RuntimeError(f"Erreur API Google Cloud TTS: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la génération audio: {str(e)}")

    def generate_voice_impact_summary(
        self,
        temperature: float = 0.7,
        max_tokens: int = 300,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        save_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Génère un résumé vocal complet (texte + audio).

        Args:
            temperature: Température du LLM pour la génération du texte
            max_tokens: Tokens maximum
            speaking_rate: Vitesse de parole (0.25 à 4.0)
            pitch: Hauteur de la voix (-20.0 à 20.0)
            save_metadata: Sauvegarder les métadonnées en JSON

        Returns:
            Dictionnaire avec toutes les informations
        """
        # Générer le résumé textuel
        summary_data = self.generate_voice_summary(
            temperature=temperature, max_tokens=max_tokens
        )

        # Générer l'audio
        audio_path = self.generate_audio(
            text=summary_data["clean_text"],
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        # Ajouter le chemin audio aux données
        summary_data["audio_path"] = audio_path
        summary_data["voice"] = self.voice_name
        summary_data["tts_provider"] = "google_cloud_api"
        summary_data["speaking_rate"] = speaking_rate
        summary_data["pitch"] = pitch
        summary_data["generated_at"] = datetime.now().isoformat()

        # Sauvegarder les métadonnées
        if save_metadata:
            metadata_path = Path(audio_path).with_suffix(".json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                # Créer une copie sans le contexte complet (trop volumineux)
                save_data = {
                    "text": summary_data["text"],
                    "clean_text": summary_data["clean_text"],
                    "post_id": summary_data["post_id"],
                    "metrics": summary_data["metrics"],
                    "audio_path": audio_path,
                    "voice": self.voice_name,
                    "tts_provider": "google_cloud_api",
                    "speaking_rate": speaking_rate,
                    "pitch": pitch,
                    "generated_at": summary_data["generated_at"],
                }
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Métadonnées sauvegardées: {metadata_path}")

        return summary_data

    def _add_context_to_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Ajoute le contexte au prompt système"""
        context_section = "\n\n# DONNÉES DU DERNIER POST\n\n"

        # Données utilisateur
        user_data = context.get("user_data", {})
        context_section += f"**Créateur:** @{user_data.get('username', 'N/A')}\n"
        context_section += f"**Followers:** {user_data.get('followers', 0):,}\n"
        context_section += (
            f"**Niche:** {user_data.get('niche', 'N/A').capitalize()}\n\n"
        )

        # Post
        post = context.get("latest_post", {})
        context_section += f"**Type:** {post.get('media_type', 'N/A').capitalize()}\n"
        context_section += f"**Caption:** {post.get('caption', 'N/A')[:100]}...\n"
        context_section += (
            f"**Hashtags:** {', '.join(post.get('hashtags', [])[:5])}\n\n"
        )

        # Métriques d'impact
        metrics = context.get("impact_metrics", {})
        context_section += "**Métriques:**\n"
        context_section += f"- Likes: {metrics.get('likes', 0):,}\n"
        context_section += f"- Commentaires: {metrics.get('comments', 0):,}\n"
        context_section += f"- Partages: {metrics.get('shares', 0):,}\n"
        context_section += f"- Sauvegardes: {metrics.get('saves', 0):,}\n"
        context_section += f"- Reach: {metrics.get('reach', 0):,}\n"
        context_section += (
            f"- Taux d'engagement: {metrics.get('engagement_rate', 0):.1f}%\n"
        )
        context_section += (
            f"- Comparé à la moyenne: {metrics.get('engagement_diff_pct', 0):+.1f}%\n"
        )
        context_section += (
            f"- Viralité (reach/followers): {metrics.get('virality_ratio', 0):.1f}%\n"
        )

        return base_prompt + context_section

    def _build_user_prompt(self, post: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Construit le prompt utilisateur"""
        prompt = (
            "Génère un résumé vocal court et impactant (maximum 150 mots) "
            "de la performance de ce post.\n\n"
        )

        prompt += f'Le post : "{post.get("caption", "")[:200]}"\n\n'

        prompt += "Concentre-toi sur :\n"
        prompt += f"1. Les chiffres clés ({metrics['likes']} likes, {metrics['comments']} commentaires, {metrics['saves']} saves)\n"
        prompt += (
            f"2. La performance vs moyenne ({metrics['engagement_diff_pct']:+.1f}%)\n"
        )
        prompt += "3. L'insight principal (pourquoi ça marche ou pas)\n"
        prompt += "4. Une action concrète à faire cette semaine\n\n"

        prompt += (
            "Rappel : Ce sera lu à voix haute, donc utilise un langage "
            "naturel et oral. Maximum 150 mots !"
        )

        return prompt

    def _clean_text_for_speech(self, text: str) -> str:
        """
        Nettoie le texte pour la synthèse vocale.

        Args:
            text: Texte brut

        Returns:
            Texte nettoyé pour l'audio
        """
        # Enlever les emojis et symboles
        clean = text

        # Enlever les markdown (**, __, etc.)
        clean = clean.replace("**", "").replace("__", "").replace("*", "")

        # Enlever les # pour les titres
        clean = clean.replace("# ", "").replace("## ", "").replace("### ", "")

        # Remplacer % par " pourcent"
        clean = clean.replace("%", " pourcent")

        # Enlever les bullet points
        clean = clean.replace("- ", "").replace("• ", "")

        # Nettoyer les espaces multiples
        clean = " ".join(clean.split())

        return clean.strip()


# Fonction utilitaire
def create_voice_impact_agent(
    rag_pipeline: RAGPipeline,
    google_api_key: str,
    voice_name: str = "fr-FR-Neural2-F",
) -> VoiceImpactAgent:
    """
    Crée une instance de VoiceImpactAgent avec Google Cloud TTS API.

    Args:
        rag_pipeline: Pipeline RAG
        google_api_key: Clé API Google Cloud
        voice_name: Nom de la voix à utiliser

    Returns:
        Instance de VoiceImpactAgent
    """
    return VoiceImpactAgent(
        rag_pipeline=rag_pipeline,
        google_api_key=google_api_key,
        voice_name=voice_name,
    )


if __name__ == "__main__":
    # Test du module
    print("=== Test du Voice Impact Agent (Google Cloud TTS API) ===\n")

    print(
        "Pour utiliser cet agent:\n"
        "1. Obtenez une clé API Google Cloud\n"
        "2. Initialisez votre RAGPipeline\n"
        "3. Créez l'agent: agent = VoiceImpactAgent(rag_pipeline, google_api_key='...')\n"
        "4. Générez le résumé: result = agent.generate_voice_impact_summary()\n"
        "5. Écoutez l'audio: result['audio_path']\n"
    )
