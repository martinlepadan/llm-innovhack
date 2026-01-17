# 📸 Instagram Coach Agent

**AI-powered Instagram coaching using RAG + LLM**

Un agent intelligent qui analyse les statistiques Instagram d'un influenceur pour fournir des conseils personnalisés d'optimisation de contenu et de croissance d'audience.

> 🏆 Projet réalisé pour le hackathon ParisInnov'Hack

## 🎯 Fonctionnalités

- ✅ **4 Modes d'agent spécialisés** : Content Analyst, Monetization, Strategy, Audience
- ✅ **API REST complète** : Endpoints FastAPI avec support streaming temps-réel
- ✅ **Voice Impact** : Résumés audio de vos posts avec Google Text-to-Speech
- ✅ **Analyse des performances** : Identifie les posts les plus performants
- ✅ **Recommandations personnalisées** : Conseils basés sur les vraies données
- ✅ **Optimisation de contenu** : Suggestions pour améliorer l'engagement
- ✅ **Stratégies de croissance** : Plans d'action pour augmenter l'audience
- ✅ **RAG (Retrieval-Augmented Generation)** : Contexte pertinent via ChromaDB
- ✅ **LLM puissant** : Featherless AI (Llama 3.1)
- ✅ **Performance optimisée** : Temps de réponse < 3 secondes

## 🆕 Nouveautés

### Version 2.0 (Janvier 2026)
- 🎙️ **Voice Impact Agent** : Résumés audio de vos posts avec Google TTS
- 🚀 **API REST FastAPI** : 8 endpoints avec support streaming
- 🤖 **4 Modes d'Agent** : Spécialisation par expertise (Content, Monetization, Strategy, Audience)
- ⚡ **Optimisations** : -40% temps de réponse, -40% coûts API
- 📊 **Endpoints Analytics** : Stats, top posts, recommendations

### Version 1.0 (Décembre 2025)
- ✅ RAG pipeline avec ChromaDB
- ✅ CLI interactive
- ✅ Jupyter notebooks

## 🚀 Quick Start

### 1. Installation

```bash
# Cloner le repo
git clone https://github.com/yourusername/llm-innovhack.git
cd llm-innovhack

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copier le fichier .env.example
cp .env.example .env

# Éditer .env et ajouter vos clés API
# FEATHERLESS_API_KEY=your_api_key_here
# GOOGLE_API_KEY=your_google_api_key (optionnel, pour Voice Impact)
```

**Pour obtenir une clé API Featherless :**
1. Aller sur [featherless.ai](https://featherless.ai)
2. Créer un compte gratuit
3. Copier votre clé API

**Optionnel - Pour Voice Impact (résumés audio) :**
1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Activer l'API Text-to-Speech
3. Créer une clé API
4. Ajouter `GOOGLE_API_KEY=your_key` dans `.env`

**Optionnel - Pour utiliser vos vraies données Instagram :**
1. Voir la section [📈 Données - Option 2](#option-2-utiliser-vos-vraies-données-instagram-instagram-graph-api)
2. Ajouter `INSTAGRAM_ACCESS_TOKEN` dans votre `.env`
3. Lancer `python fetch_instagram_data.py` pour récupérer vos données

### 3. Lancer l'agent

#### Option A: Interface CLI (ligne de commande)

```bash
# Mode interactif (chat)
python main.py

# Poser une question unique
python main.py --question "Quels sont mes posts les plus performants ?"

# Lancer la démo
python main.py --demo

# Voir les statistiques
python main.py --stats
```

#### Option B: Serveur API (FastAPI)

```bash
# Démarrer le serveur
uvicorn api:app --reload --port 8000

# Le serveur sera accessible à http://localhost:8000
# Documentation API: http://localhost:8000/docs
```

**Endpoints disponibles :**
- `POST /api/chat` - Chat non-streaming (réponse complète)
- `POST /api/chat/stream` - Chat streaming (temps-réel)
- `GET /api/stats` - Statistiques du compte
- `GET /api/modes` - Liste des modes d'agent disponibles
- `POST /api/recommendations/{focus}` - Recommandations ciblées
- `GET /api/top-posts` - Top posts par métrique
- `GET /health` - Health check

**Exemple d'utilisation de l'API :**

```bash
# Chat simple
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quels sont mes meilleurs posts ?", "mode": "content_analyst"}'

# Obtenir les stats
curl "http://localhost:8000/api/stats"

# Recommandations ciblées
curl -X POST "http://localhost:8000/api/recommendations/content"
```

## 🤖 Modes d'Agent Spécialisés

L'agent propose **4 modes d'expertise** adaptés à vos besoins :

### 📊 Content Analyst
Analyse détaillée de vos performances Instagram.
```python
agent.ask("Analyse mes meilleurs posts de la semaine", mode="content_analyst")
```
**Expertise :** Métriques, engagement, types de contenu performants

### 💰 Monetization Advisor
Conseils pour monétiser votre compte et obtenir des partenariats.
```python
agent.ask("Comment puis-je monétiser mon compte ?", mode="monetization")
```
**Expertise :** Partenariats, tarification, stratégies de revenus

### 🎯 Content Strategy
Planification stratégique de contenu et idées créatives.
```python
agent.ask("Quelles idées de posts pour la semaine prochaine ?", mode="content_strategy")
```
**Expertise :** Planning éditorial, tendances, créativité

### 👥 Audience Insights
Compréhension approfondie de votre communauté.
```python
agent.ask("Qui sont mes followers les plus engagés ?", mode="audience")
```
**Expertise :** Démographie, comportements, interactions

### 🎙️ Voice Impact (Nouveau!)

Génère des résumés **audio** de vos performances avec Google Text-to-Speech.

```bash
# Nécessite GOOGLE_API_KEY dans .env
python -c "from src.voice_impact_agent_google_api import VoiceImpactAgent; agent = VoiceImpactAgent(); agent.generate_voice_summary()"
```

**Caractéristiques :**
- Résumés courts (30-60 secondes)
- Voix françaises naturelles (Neural2, Wavenet, Studio)
- Format conversationnel et oral
- Fichiers audio sauvegardés dans `output/voice_summaries/`
- Analyse du dernier post publié

**Cas d'usage :** Écouter vos performances pendant vos déplacements, partager sur Instagram Stories, créer du contenu audio.

## 📊 Utilisation du Notebook

Pour une démo interactive avec visualisations :

```bash
jupyter notebook notebooks/demo.ipynb
```

Le notebook inclut :
- 📈 Graphiques de performance
- 🎯 Exemples de questions pré-configurées
- 💾 Export de rapports
- 🔬 Analyse détaillée

## 🏗️ Architecture

```
instagram-coach-agent/
├── api.py                                    # FastAPI REST server
├── main.py                                   # Interface CLI
├── data/
│   ├── sample_posts.json                    # 30+ posts Instagram mockés
│   └── influencer_profile.json              # Profil de l'influenceur
├── src/
│   ├── agent.py                             # Agent principal
│   ├── agent_modes.py                       # Routing des modes spécialisés
│   ├── rag_pipeline.py                      # Pipeline RAG complet
│   ├── llm_client.py                        # Client Featherless AI
│   ├── vector_store.py                      # ChromaDB vector store
│   ├── embeddings.py                        # Génération d'embeddings
│   ├── voice_impact_agent_google_api.py     # Agent Voice Impact (TTS)
│   ├── data_transformer.py                  # Transformation de données
│   ├── config.py                            # Configuration
│   ├── prompts/                             # Prompts système par mode
│   │   ├── content_analyst_prompt.txt
│   │   ├── monetization_advisor_prompt.txt
│   │   ├── content_strategy_prompt.txt
│   │   ├── audience_insights_prompt.txt
│   │   └── voice_impact_summary_prompt.txt
│   └── utils/
│       └── prompt_manager.py                # Gestion des prompts
├── notebooks/
│   └── demo.ipynb                           # Démo interactive
├── tests/                                   # Tests unitaires
├── output/                                  # Sorties (API, voice)
├── chroma_db/                               # Persistence vector store
└── requirements.txt
```

## 🧠 Comment ça marche ?

### Pipeline RAG

1. **Indexation** (au démarrage)
   - Chargement des posts Instagram depuis JSON
   - Génération d'embeddings avec sentence-transformers
   - Stockage dans ChromaDB (base vectorielle)

2. **Retrieval** (lors d'une question)
   - Embedding de la question utilisateur
   - Recherche sémantique des posts pertinents
   - Sélection des top-K posts similaires

3. **Génération** (réponse LLM)
   - Construction d'un prompt enrichi avec contexte
   - Appel à Featherless AI (Llama 3.1)
   - Génération de conseils personnalisés

### Exemple de flow

```python
from agent import InstagramCoachAgent

# 1. Initialiser l'agent
agent = InstagramCoachAgent()

# 2. Poser une question
response = agent.ask("Comment améliorer mon engagement ?")

# 3. L'agent va :
#    - Récupérer vos 5 posts les plus pertinents
#    - Analyser leurs métriques
#    - Générer des recommandations basées sur VOS données
```

## 💡 Exemples de questions

### 📊 Content Analyst
```python
"Quels sont mes posts les plus performants ?"
"Quel type de contenu génère le plus d'engagement ?"
"Compare les performances de mes reels vs photos"
"Quels posts ont le meilleur taux de sauvegarde ?"
```

### 💰 Monetization Advisor
```python
"Comment puis-je monétiser mon compte avec 15K followers ?"
"Combien devrais-je facturer pour un partenariat ?"
"Quelles marques pourraient être intéressées par mon profil ?"
"Comment créer un media kit efficace ?"
```

### 🎯 Content Strategy
```python
"Quelles idées de posts pour la semaine prochaine ?"
"Comment créer un calendrier éditorial efficace ?"
"À quelle fréquence devrais-je publier ?"
"Quels sujets tendances exploiter dans ma niche ?"
```

### 👥 Audience Insights
```python
"Qui sont mes followers les plus engagés ?"
"À quel moment ma communauté est-elle la plus active ?"
"Comment améliorer l'interaction avec mes followers ?"
"Quelle est la démographie de mon audience ?"
```

## 🔧 Technologies

| Composant | Technologie | Pourquoi |
|-----------|-------------|----------|
| **LLM** | Featherless AI (Llama 3.1 8B) | Rapide, gratuit, performant |
| **Embeddings** | sentence-transformers | Local, gratuit, multilingual |
| **Vector DB** | ChromaDB | Simple, local, pas de setup serveur |
| **API Framework** | FastAPI + Uvicorn | Async, rapide, auto-documentation |
| **TTS** | Google Cloud Text-to-Speech | Voix naturelles, multi-langues |
| **Framework** | Python 3.10+ | Écosystème ML mature |
| **Interface** | CLI + API + Jupyter | Multi-plateforme, flexible |

## 📈 Données

### Option 1: Utiliser les données de démonstration (par défaut)

Le projet inclut des données mockées pour démarrer rapidement:

- ✅ 30 posts Instagram réalistes
- ✅ Profil d'influenceur lifestyle (45K followers)
- ✅ Métriques complètes (likes, comments, saves, reach, etc.)
- ✅ Mix de reels, photos, carousels

### Option 2: Utiliser vos vraies données Instagram (Instagram Graph API)

Pour analyser votre propre compte Instagram, vous pouvez récupérer vos vraies données via l'Instagram Graph API.

#### Prérequis

1. **Compte Instagram Business ou Creator**
2. **Page Facebook** connectée à votre Instagram
3. **Application Facebook** avec Instagram Graph API activé
4. **Access Token** avec les permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_show_list`

#### Configuration

```bash
# 1. Obtenez votre access token
# Allez sur https://developers.facebook.com/apps/
# Créez ou sélectionnez votre app
# Ajoutez le produit "Instagram Graph API"
# Générez un User Access Token

# 2. Ajoutez le token à votre .env
echo "INSTAGRAM_ACCESS_TOKEN=your_token_here" >> .env
```

#### Récupération des données

```bash
# Tester la connexion
python fetch_instagram_data.py --test

# Récupérer 30 posts (par défaut)
python fetch_instagram_data.py

# Récupérer un nombre personnalisé de posts
python fetch_instagram_data.py --limit 50

# Avec un token personnalisé
python fetch_instagram_data.py --token YOUR_ACCESS_TOKEN

# Sauvegarder dans un répertoire personnalisé
python fetch_instagram_data.py --output my_data/
```

Le script va:
1. ✅ Se connecter à votre compte Instagram via l'API
2. ✅ Récupérer votre profil et vos posts
3. ✅ Transformer les données au format attendu par le modèle
4. ✅ Sauvegarder dans `data/` (ou répertoire personnalisé)

Ensuite, lancez simplement `python main.py` pour utiliser vos vraies données!

#### Guide complet d'obtention de l'access token

<details>
<summary>📖 Cliquez pour voir le guide détaillé</summary>

1. **Créer une application Facebook**
   - Allez sur https://developers.facebook.com/apps/
   - Cliquez sur "Create App"
   - Choisissez "Business" comme type
   - Donnez un nom à votre app

2. **Ajouter Instagram Graph API**
   - Dans votre app, allez dans "Add Product"
   - Trouvez "Instagram Graph API" et cliquez "Set Up"

3. **Générer un access token**
   - Allez dans "Tools" > "Graph API Explorer"
   - Sélectionnez votre app
   - Ajoutez les permissions: `instagram_basic`, `instagram_manage_insights`, `pages_show_list`
   - Cliquez "Generate Access Token"
   - Copiez le token

4. **Prolonger la durée du token (optionnel)**
   - Les tokens expirent après 1 heure par défaut
   - Pour un token longue durée (60 jours):
     ```bash
     curl -G "https://graph.facebook.com/v18.0/oauth/access_token" \
       -d "grant_type=fb_exchange_token" \
       -d "client_id=YOUR_APP_ID" \
       -d "client_secret=YOUR_APP_SECRET" \
       -d "fb_exchange_token=SHORT_LIVED_TOKEN"
     ```

5. **Tester le token**
   ```bash
   python fetch_instagram_data.py --test
   ```

</details>

### Format des posts

```json
{
  "id": "post_001",
  "caption": "Ma routine matinale...",
  "media_type": "reel",
  "timestamp": "2025-01-10T08:30:00Z",
  "metrics": {
    "likes": 1250,
    "comments": 87,
    "shares": 45,
    "saves": 320,
    "reach": 15000,
    "impressions": 18500,
    "engagement_rate": 11.3
  },
  "hashtags": ["productivity", "morning"]
}
```

## 🎓 Utilisation Avancée

### Sélection du mode d'agent

```python
from src.agent import InstagramCoachAgent

agent = InstagramCoachAgent()

# Mode Content Analyst
response = agent.ask("Analyse mes meilleurs posts", mode="content_analyst")

# Mode Monetization
response = agent.ask("Combien facturer ?", mode="monetization")

# Mode Strategy
response = agent.ask("Idées de contenu", mode="content_strategy")

# Mode Audience
response = agent.ask("Qui sont mes followers ?", mode="audience")
```

### Personnaliser les paramètres LLM

```python
agent.ask(
    "Votre question",
    mode="content_analyst",
    temperature=0.9,      # Plus créatif (0.0-1.0)
    max_tokens=600,       # Réponse plus longue
    n_posts=10            # Plus de contexte
)
```

### Utiliser vos propres données

```python
agent.load_data(
    posts_path=Path("mes_posts.json"),
    profile_path=Path("mon_profil.json"),
    force_reload=True
)
```

### Méthodes helpers

```python
# Recommandations ciblées
agent.get_recommendations(focus="content")   # Optimisation contenu
agent.get_recommendations(focus="growth")    # Croissance
agent.get_recommendations(focus="engagement") # Engagement

# Analyse par type
agent.analyze_content_type("reel")  # Performance des reels

# Suggestions
agent.suggest_hashtags()            # Hashtags recommandés
agent.get_posting_schedule()        # Planning optimal
```

### API Streaming vs Non-Streaming

**Non-streaming** (réponse complète) :
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "Analyse mes posts", "mode": "content_analyst"}
)
print(response.json()["response"])
```

**Streaming** (temps-réel) :
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={"message": "Analyse mes posts", "mode": "content_analyst", "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### Voice Impact - Génération audio

```python
from src.voice_impact_agent_google_api import VoiceImpactAgent

# Initialiser l'agent
voice_agent = VoiceImpactAgent()

# Générer un résumé audio du dernier post
audio_path = voice_agent.generate_voice_summary()
print(f"Audio généré : {audio_path}")

# Personnaliser la voix
voice_agent.generate_voice_summary(
    voice_name="fr-FR-Neural2-A",  # Voix féminine
    speaking_rate=1.1,              # Plus rapide
    pitch=2.0                       # Ton plus aigu
)
```

## 🐛 Troubleshooting

### Erreur "API key not found"
```bash
# Vérifier que .env existe et contient :
FEATHERLESS_API_KEY=your_actual_key
# Pour Voice Impact :
GOOGLE_API_KEY=your_google_key
```

### Erreur d'import ChromaDB
```bash
pip install --upgrade chromadb
```

### ModuleNotFoundError
```bash
# Vérifier que vous êtes dans le bon environnement
which python  # Doit pointer vers venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Embeddings trop lents
```python
# Dans .env, utiliser un modèle plus petit :
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Erreur Google Cloud TTS
```bash
# Vérifier que l'API Text-to-Speech est activée
# Dans Google Cloud Console > API & Services > Enable APIs
# Chercher "Cloud Text-to-Speech API" et l'activer

# Vérifier la clé API
echo $GOOGLE_API_KEY  # Doit afficher votre clé
```

### Erreur FastAPI / Uvicorn
```bash
# Port déjà utilisé
uvicorn api:app --reload --port 8001  # Utiliser un autre port

# Erreur CORS
# Vérifier que l'origine est autorisée dans api.py > allow_origins
```

### Mode d'agent non reconnu
```python
# Modes valides : content_analyst, monetization, content_strategy, audience
# Vérifier l'orthographe et les underscores
agent.ask("Votre question", mode="content_analyst")  # ✅
agent.ask("Votre question", mode="content analyst")  # ❌
```

## 🔌 API Reference

L'API FastAPI offre plusieurs endpoints pour intégrer l'agent dans vos applications.

### Base URL
```
http://localhost:8000
```

### Endpoints Disponibles

#### POST `/api/chat`
Chat non-streaming avec réponse complète.

**Request:**
```json
{
  "message": "Quels sont mes meilleurs posts ?",
  "mode": "content_analyst",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "response": "Voici une analyse de vos meilleurs posts...",
  "mode": "content_analyst",
  "processing_time": 2.3
}
```

#### POST `/api/chat/stream`
Chat streaming pour réponses en temps-réel.

**Request:** (identique à `/api/chat` avec `"stream": true`)

**Response:** Server-Sent Events (SSE)
```
data: {"chunk": "Voici"}
data: {"chunk": " une"}
data: {"chunk": " analyse..."}
```

#### GET `/api/stats`
Statistiques globales du compte.

**Response:**
```json
{
  "total_posts": 30,
  "total_likes": 45230,
  "total_comments": 2140,
  "avg_engagement_rate": 8.5,
  "top_performing_type": "reel",
  "follower_count": 15000
}
```

#### GET `/api/modes`
Liste des modes d'agent disponibles.

**Response:**
```json
{
  "modes": [
    {
      "id": "content_analyst",
      "name": "Content Analyst",
      "description": "Analyse de performance et métriques",
      "icon": "📊"
    },
    {
      "id": "monetization",
      "name": "Monetization Advisor",
      "description": "Conseils de monétisation",
      "icon": "💰"
    },
    // ... autres modes
  ]
}
```

#### POST `/api/recommendations/{focus}`
Recommandations ciblées (focus: content, growth, engagement).

**Response:**
```json
{
  "focus": "content",
  "recommendations": [
    "Publiez plus de reels, ils génèrent 2x plus d'engagement",
    "Utilisez des hashtags de niche (#lifestylefr)",
    // ... autres recommandations
  ]
}
```

#### GET `/api/top-posts?metric=engagement_rate&limit=5`
Top posts par métrique (likes, comments, engagement_rate, saves, reach).

**Response:**
```json
{
  "metric": "engagement_rate",
  "posts": [
    {
      "id": "post_001",
      "caption": "Ma routine matinale...",
      "engagement_rate": 11.3,
      "likes": 1250,
      // ... autres métriques
    }
    // ... autres posts
  ]
}
```

#### GET `/health`
Health check de l'API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Documentation Interactive

Une fois le serveur démarré, accédez à la documentation Swagger :
```
http://localhost:8000/docs
```

Ou à la documentation ReDoc :
```
http://localhost:8000/redoc
```

## ⚡ Performance & Optimisations

### Optimisations Appliquées (Phase 1)

Ce projet a été optimisé pour maximiser la réactivité du chatbot:

- ✅ **Prompt système réduit de 75%** (~1000 → ~250 tokens) pour génération plus rapide
- ✅ **Retrieval optimisé** (3 posts au lieu de 5) pour réduction de 40% du temps de recherche
- ✅ **Temps de réponse réduit de 30-40%** (de 3-5s à 2-3s)
- ✅ **Coûts API réduits de 40%** par requête

**Résultat:** Latence < 3 secondes (objectif du cahier des charges ✅)

📖 Voir [OPTIMIZATIONS.md](OPTIMIZATIONS.md) pour les détails complets des optimisations et les métriques.

### Métriques de Performance

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps de réponse | 3-5s | 2-3s | **-40%** |
| Tokens/requête | 1500-2000 | 800-1200 | **-40%** |
| Posts récupérés | 5 | 3 | **-40%** |
| Coût par requête | 100% | ~60% | **-40%** |

## 📝 License

MIT License - Libre d'utilisation