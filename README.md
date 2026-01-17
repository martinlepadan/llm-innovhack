# 📸 Instagram Coach Agent

**AI-powered Instagram coaching using RAG + LLM**

Un agent intelligent qui analyse les statistiques Instagram d'un influenceur pour fournir des conseils personnalisés d'optimisation de contenu et de croissance d'audience.

> 🏆 Projet réalisé pour le hackathon ParisInnov'Hack

## 🎯 Fonctionnalités

- ✅ **Analyse des performances** : Identifie les posts les plus performants
- ✅ **Recommandations personnalisées** : Conseils basés sur les vraies données
- ✅ **Optimisation de contenu** : Suggestions pour améliorer l'engagement
- ✅ **Stratégies de croissance** : Plans d'action pour augmenter l'audience
- ✅ **RAG (Retrieval-Augmented Generation)** : Contexte pertinent via ChromaDB
- ✅ **LLM puissant** : Featherless AI (Llama 3.1)

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

# Éditer .env et ajouter votre clé API Featherless
# FEATHERLESS_API_KEY=your_api_key_here
```

**Pour obtenir une clé API Featherless :**
1. Aller sur [featherless.ai](https://featherless.ai)
2. Créer un compte gratuit
3. Copier votre clé API

**Optionnel - Pour utiliser vos vraies données Instagram :**
1. Voir la section [📈 Données - Option 2](#option-2-utiliser-vos-vraies-données-instagram-instagram-graph-api)
2. Ajouter `INSTAGRAM_ACCESS_TOKEN` dans votre `.env`
3. Lancer `python fetch_instagram_data.py` pour récupérer vos données

### 3. Lancer l'agent

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
├── data/
│   ├── sample_posts.json         # 30 posts Instagram mockés
│   └── influencer_profile.json   # Profil de l'influenceur
├── src/
│   ├── config.py                 # Configuration
│   ├── embeddings.py             # Génération d'embeddings
│   ├── vector_store.py           # ChromaDB vector store
│   ├── llm_client.py             # Client Featherless AI
│   ├── rag_pipeline.py           # Pipeline RAG complet
│   └── agent.py                  # Agent principal
├── notebooks/
│   └── demo.ipynb                # Démo interactive
├── main.py                       # CLI
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

```python
# Analyse de performance
"Quels sont mes posts les plus performants ?"
"Quel type de contenu fonctionne le mieux ?"

# Optimisation
"Comment améliorer mon taux d'engagement ?"
"Quels hashtags devrais-je utiliser ?"

# Stratégie
"Quelle stratégie pour augmenter mes followers ?"
"À quelle fréquence devrais-je publier ?"

# Timing
"Quels sont les meilleurs moments pour publier ?"
"Comment planifier mon contenu pour le mois prochain ?"
```

## 🔧 Technologies

| Composant | Technologie | Pourquoi |
|-----------|-------------|----------|
| **LLM** | Featherless AI (Llama 3.1 8B) | Rapide, gratuit, performant |
| **Embeddings** | sentence-transformers | Local, gratuit, multilingual |
| **Vector DB** | ChromaDB | Simple, local, pas de setup serveur |
| **Framework** | Python 3.10+ | Écosystème ML mature |
| **Interface** | CLI + Jupyter | Démo facile |

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

### Personnaliser les paramètres LLM

```python
agent.ask(
    "Votre question",
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

## 🐛 Troubleshooting

### Erreur "API key not found"
```bash
# Vérifier que .env existe et contient :
FEATHERLESS_API_KEY=your_actual_key
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