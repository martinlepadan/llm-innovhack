# 📘 Documentation Backend - Intégration du Système Instagram Coach

**Pour :** Développeur Backend
**Version :** 1.0
**Dernière mise à jour :** 2026-01-17

---

## 🎯 Vue d'Ensemble

Ce système fournit un agent IA spécialisé en coaching Instagram avec **4 modes d'expertise** :
1. **Analyse de Performance** (content_analyst)
2. **Monétisation** (monetization)
3. **Stratégie de Contenu** (strategy)
4. **Analyse d'Audience** (audience)

Le système utilise **RAG (Retrieval-Augmented Generation)** pour analyser les posts Instagram et fournir des réponses basées sur les données réelles.

---

## 📦 Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les variables d'environnement
cp .env.example .env

# 3. Éditer .env avec vos clés API
# FEATHERLESS_API_KEY=votre_clé_ici
```

---

## 🚀 Quick Start

### Utilisation Basique

```python
from agent import InstagramCoachAgent, AgentMode

# Initialiser l'agent
agent = InstagramCoachAgent()

# Poser une question (sans streaming)
response = agent.ask(
    question="Quels sont mes meilleurs posts ?",
    mode=AgentMode.CONTENT_ANALYST,
    stream=False  # IMPORTANT pour récupérer la réponse complète
)

print(response)  # String de la réponse
```

### Avec Streaming (Recommandé)

```python
# Poser une question avec streaming
result = agent.ask(
    question="Quels sont mes meilleurs posts ?",
    mode=AgentMode.CONTENT_ANALYST,
    stream=True  # Active le streaming
)

# result contient un générateur
# Attention : dans ask(), le streaming est déjà géré et affiché
# Pour une API, utilisez la fonction de bas niveau (voir section API)
```

---

## 🏗️ Architecture du Système

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vue/etc)                 │
│          Envoie: {question, mode, stream: true/false}       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI/Flask)                  │
│  • Reçoit la requête                                        │
│  • Appelle InstagramCoachAgent.ask() ou generate_with_mode()│
│  • Gère le streaming si nécessaire                          │
│  • Retourne la réponse                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Appel Python
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SYSTÈME INSTAGRAM COACH (Ce Code)              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  InstagramCoachAgent (agent.py)                     │   │
│  │  • Interface principale                             │   │
│  │  • Gère les modes                                   │   │
│  │  • Méthode ask(question, mode, stream)              │   │
│  └───────────────────┬─────────────────────────────────┘   │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  agent_modes.py                                     │   │
│  │  • generate_with_mode(rag_pipeline, question, mode) │   │
│  │  • Charge le prompt spécialisé                      │   │
│  └───────────────────┬─────────────────────────────────┘   │
│                      │                                      │
│         ┌────────────┴────────────┐                        │
│         ▼                         ▼                        │
│  ┌─────────────┐         ┌──────────────────┐             │
│  │ RAG Pipeline│         │  PromptManager   │             │
│  │ • Récupère  │         │  • Charge prompts│             │
│  │   les posts │         │  • Ajoute context│             │
│  │ • Vectorise │         └──────────────────┘             │
│  │ • Query DB  │                                          │
│  └──────┬──────┘                                          │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                          │
│  │  LLM Client │                                          │
│  │  • Appelle  │                                          │
│  │    l'API LLM│                                          │
│  │  • Streaming│                                          │
│  └─────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Intégration Backend

### Option 1 : API REST avec FastAPI (Sans Streaming)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Import du système Instagram Coach
sys.path.insert(0, str(Path(__file__).parent / "src"))
from agent import InstagramCoachAgent, AgentMode

app = FastAPI()

# Initialiser l'agent au démarrage (singleton)
agent = InstagramCoachAgent()

# Modèle de requête
class QuestionRequest(BaseModel):
    question: str
    mode: str = "content_analyst"  # défaut
    n_posts: int = 3

# Modèle de réponse
class QuestionResponse(BaseModel):
    question: str
    mode: str
    response: str

# Mapping mode string → enum
MODE_MAP = {
    "content_analyst": AgentMode.CONTENT_ANALYST,
    "monetization": AgentMode.MONETIZATION,
    "strategy": AgentMode.STRATEGY,
    "audience": AgentMode.AUDIENCE,
}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    """Endpoint pour poser une question"""

    # Valider le mode
    if req.mode not in MODE_MAP:
        raise HTTPException(400, f"Mode invalide: {req.mode}")

    try:
        # Appeler l'agent SANS streaming
        response = agent.ask(
            question=req.question,
            mode=MODE_MAP[req.mode],
            n_posts=req.n_posts,
            stream=False  # ← IMPORTANT : désactive le streaming
        )

        return QuestionResponse(
            question=req.question,
            mode=req.mode,
            response=response
        )

    except Exception as e:
        raise HTTPException(500, str(e))

# Lancer avec: uvicorn main:app --reload
```

**Tester :**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quels sont mes meilleurs posts ?",
    "mode": "content_analyst"
  }'
```

---

### Option 2 : API REST avec Streaming (Server-Sent Events)

**IMPORTANT :** Le streaming est crucial pour une bonne UX car les réponses peuvent prendre du temps.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from agent_modes import generate_with_mode, AgentMode
from rag_pipeline import get_rag_pipeline

app = FastAPI()

# Initialiser le pipeline RAG (singleton)
rag_pipeline = get_rag_pipeline()
rag_pipeline.load_data()

MODE_MAP = {
    "content_analyst": AgentMode.CONTENT_ANALYST,
    "monetization": AgentMode.MONETIZATION,
    "strategy": AgentMode.STRATEGY,
    "audience": AgentMode.AUDIENCE,
}

class QuestionRequest(BaseModel):
    question: str
    mode: str = "content_analyst"
    n_posts: int = 3

@app.post("/ask/stream")
async def ask_with_stream(req: QuestionRequest):
    """
    Endpoint avec streaming via Server-Sent Events (SSE).
    Le front reçoit la réponse chunk par chunk en temps réel.
    """

    async def event_generator():
        """Générateur pour SSE"""
        try:
            # Appeler generate_with_mode avec streaming
            result = generate_with_mode(
                rag_pipeline=rag_pipeline,
                question=req.question,
                mode=MODE_MAP.get(req.mode, AgentMode.CONTENT_ANALYST),
                n_results=req.n_posts,
                stream=True  # ← Active le streaming
            )

            # Envoyer les métadonnées d'abord
            yield f"data: {json.dumps({'type': 'metadata', 'mode': req.mode})}\n\n"

            # Streamer la réponse chunk par chunk
            for chunk in result['response_stream']:
                # Format SSE
                data = json.dumps({
                    'type': 'chunk',
                    'content': chunk
                })
                yield f"data: {data}\n\n"

            # Signal de fin
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            # En cas d'erreur
            error_data = json.dumps({
                'type': 'error',
                'message': str(e)
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Pour nginx
        }
    )

# Lancer avec: uvicorn main:app --reload
```

**Consommer côté Frontend (JavaScript) :**

```javascript
const eventSource = new EventSource('http://localhost:8000/ask/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Quels sont mes meilleurs posts ?",
    mode: "content_analyst"
  })
});

let fullResponse = "";

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'chunk') {
    fullResponse += data.content;
    // Afficher le chunk dans l'UI
    updateUI(data.content);
  } else if (data.type === 'done') {
    console.log("Streaming terminé");
    eventSource.close();
  } else if (data.type === 'error') {
    console.error("Erreur:", data.message);
    eventSource.close();
  }
};
```

---

### Option 3 : WebSocket (Streaming Bidirectionnel)

```python
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from agent_modes import generate_with_mode, AgentMode
from rag_pipeline import get_rag_pipeline

app = FastAPI()
rag_pipeline = get_rag_pipeline()
rag_pipeline.load_data()

MODE_MAP = {
    "content_analyst": AgentMode.CONTENT_ANALYST,
    "monetization": AgentMode.MONETIZATION,
    "strategy": AgentMode.STRATEGY,
    "audience": AgentMode.AUDIENCE,
}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket pour chat en temps réel avec streaming"""
    await websocket.accept()

    try:
        while True:
            # Recevoir la question du client
            data = await websocket.receive_text()
            request = json.loads(data)

            question = request.get('question')
            mode = request.get('mode', 'content_analyst')
            n_posts = request.get('n_posts', 3)

            # Envoyer confirmation de réception
            await websocket.send_json({
                'type': 'processing',
                'message': 'Analyse en cours...'
            })

            # Générer avec streaming
            result = generate_with_mode(
                rag_pipeline=rag_pipeline,
                question=question,
                mode=MODE_MAP.get(mode, AgentMode.CONTENT_ANALYST),
                n_results=n_posts,
                stream=True
            )

            # Streamer chaque chunk
            for chunk in result['response_stream']:
                await websocket.send_json({
                    'type': 'chunk',
                    'content': chunk
                })

            # Signal de fin
            await websocket.send_json({
                'type': 'done'
            })

    except WebSocketDisconnect:
        print("Client déconnecté")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })
```

**Consommer côté Frontend (JavaScript) :**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  // Envoyer une question
  ws.send(JSON.stringify({
    question: "Quels sont mes meilleurs posts ?",
    mode: "content_analyst",
    n_posts: 5
  }));
};

let fullResponse = "";

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'processing':
      console.log("En cours...");
      break;
    case 'chunk':
      fullResponse += data.content;
      updateUI(data.content);  // Afficher chunk par chunk
      break;
    case 'done':
      console.log("Terminé !");
      break;
    case 'error':
      console.error("Erreur:", data.message);
      break;
  }
};
```

---

## 📊 Utilisation de Bas Niveau (Recommandé pour Backend)

Pour plus de contrôle, utilisez directement `generate_with_mode()` :

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_modes import generate_with_mode, AgentMode
from rag_pipeline import get_rag_pipeline

# Initialiser le pipeline RAG (faire une seule fois au démarrage)
rag_pipeline = get_rag_pipeline()
rag_pipeline.load_data()

# Fonction pour générer une réponse
def get_instagram_advice(question: str, mode: str = "content_analyst", stream: bool = False):
    """
    Génère un conseil Instagram.

    Args:
        question: Question de l'utilisateur
        mode: Mode d'agent (content_analyst, monetization, strategy, audience)
        stream: Si True, retourne un générateur pour streaming

    Returns:
        Si stream=False: dict avec 'response' (string)
        Si stream=True: dict avec 'response_stream' (generator)
    """
    mode_map = {
        "content_analyst": AgentMode.CONTENT_ANALYST,
        "monetization": AgentMode.MONETIZATION,
        "strategy": AgentMode.STRATEGY,
        "audience": AgentMode.AUDIENCE,
    }

    result = generate_with_mode(
        rag_pipeline=rag_pipeline,
        question=question,
        mode=mode_map.get(mode, AgentMode.CONTENT_ANALYST),
        n_results=3,  # Nombre de posts à analyser
        temperature=0.5,  # Créativité (0-1)
        max_tokens=1000,  # Longueur max de la réponse
        stream=stream
    )

    return result

# Exemple sans streaming
result = get_instagram_advice(
    "Quels sont mes meilleurs posts ?",
    mode="content_analyst",
    stream=False
)
print(result['response'])

# Exemple avec streaming
result = get_instagram_advice(
    "Comment monétiser mon compte ?",
    mode="monetization",
    stream=True
)
for chunk in result['response_stream']:
    print(chunk, end='', flush=True)
```

---

## 🎛️ Les 4 Modes Disponibles

### 1. content_analyst (Analyse de Performance)
**Quand l'utiliser :** Questions sur métriques, performance, engagement

```python
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question="Quels sont mes posts les plus performants ?",
    mode=AgentMode.CONTENT_ANALYST
)
```

**Exemples de questions :**
- "Quels sont mes meilleurs posts ?"
- "Pourquoi mon engagement a baissé ?"
- "Quel type de contenu fonctionne le mieux ?"

---

### 2. monetization (Monétisation)
**Quand l'utiliser :** Questions sur revenus, partenariats, prix

```python
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question="Combien facturer pour un post sponsorisé ?",
    mode=AgentMode.MONETIZATION
)
```

**Exemples de questions :**
- "Combien facturer pour un post sponsorisé ?"
- "Quelles marques devrais-je contacter ?"
- "Comment diversifier mes revenus ?"

---

### 3. strategy (Stratégie de Contenu)
**Quand l'utiliser :** Questions sur planning, idées, création

```python
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question="Quelles idées de contenu pour cette semaine ?",
    mode=AgentMode.STRATEGY
)
```

**Exemples de questions :**
- "Quelles idées de contenu pour cette semaine ?"
- "Comment planifier mon calendrier éditorial ?"
- "Comment rendre mon contenu viral ?"

---

### 4. audience (Analyse d'Audience)
**Quand l'utiliser :** Questions sur communauté, followers, démographie

```python
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question="Qui sont mes followers ?",
    mode=AgentMode.AUDIENCE
)
```

**Exemples de questions :**
- "Qui sont vraiment mes followers ?"
- "Mon audience achèterait-elle mes produits ?"
- "Comment attirer plus de followers qualifiés ?"

---

## 🔧 Paramètres Disponibles

### `generate_with_mode()` - Fonction de Bas Niveau

```python
from agent_modes import generate_with_mode, AgentMode

result = generate_with_mode(
    rag_pipeline,      # Instance du RAG pipeline
    question="...",    # Question de l'utilisateur
    mode=AgentMode.CONTENT_ANALYST,  # Mode d'agent
    n_results=3,       # Nombre de posts à récupérer (3-10 recommandé)
    temperature=0.5,   # Créativité: 0=déterministe, 1=créatif
    max_tokens=1000,   # Longueur max de la réponse
    stream=False       # True pour streaming, False pour réponse complète
)
```

**Retour si `stream=False` :**
```python
{
    "mode": "content_analyst",
    "mode_description": "📊 Analyse de Performance...",
    "response": "Voici vos meilleurs posts...",  # String complète
    "relevant_posts": [...],  # Posts utilisés pour la réponse
    "question": "..."
}
```

**Retour si `stream=True` :**
```python
{
    "mode": "content_analyst",
    "mode_description": "📊 Analyse de Performance...",
    "response_stream": <generator>,  # Générateur de chunks
    "relevant_posts": [...],
    "question": "..."
}

# Utilisation du générateur
for chunk in result['response_stream']:
    print(chunk, end='', flush=True)
```

---

## 📁 Structure des Données

### Format de Requête (Frontend → Backend)

```json
{
  "question": "Quels sont mes meilleurs posts ?",
  "mode": "content_analyst",
  "n_posts": 5,
  "stream": true
}
```

### Format de Réponse (Backend → Frontend)

**Sans streaming :**
```json
{
  "question": "Quels sont mes meilleurs posts ?",
  "mode": "content_analyst",
  "mode_description": "📊 Analyse de Performance",
  "response": "D'après l'analyse de vos posts...",
  "n_posts_analyzed": 5
}
```

**Avec streaming (SSE) :**
```
data: {"type": "metadata", "mode": "content_analyst"}

data: {"type": "chunk", "content": "D'après"}

data: {"type": "chunk", "content": " l'analyse"}

data: {"type": "chunk", "content": " de vos"}

...

data: {"type": "done"}
```

---

## ⚙️ Configuration

### Variables d'Environnement (.env)

```bash
# API Key pour le LLM (Featherless)
FEATHERLESS_API_KEY=your_api_key_here

# Optionnel : Chemins des données
POSTS_DATA_PATH=data/posts.json
PROFILE_DATA_PATH=data/profile.json

# Optionnel : Configuration LLM
LLM_MODEL=meta-llama/Meta-Llama-3.1-405B-Instruct
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=1000
```

### Charger les Données Instagram

```python
from rag_pipeline import get_rag_pipeline

# Méthode 1 : Chargement automatique (depuis config)
rag_pipeline = get_rag_pipeline()
rag_pipeline.load_data()

# Méthode 2 : Chemins personnalisés
rag_pipeline.load_data(
    posts_path="custom/path/posts.json",
    profile_path="custom/path/profile.json"
)

# Méthode 3 : Recharger les données
rag_pipeline.load_data(force_reload=True)
```

---

## 🔒 Gestion d'Erreurs

```python
from fastapi import HTTPException

@app.post("/ask")
async def ask(req: QuestionRequest):
    try:
        # Validation du mode
        if req.mode not in MODE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"Mode invalide. Modes valides: {list(MODE_MAP.keys())}"
            )

        # Validation de la question
        if not req.question or len(req.question) < 3:
            raise HTTPException(
                status_code=400,
                detail="Question trop courte"
            )

        # Génération de la réponse
        result = generate_with_mode(...)

        return result

    except FileNotFoundError as e:
        # Données Instagram manquantes
        raise HTTPException(
            status_code=503,
            detail="Données Instagram non disponibles. Veuillez charger les données."
        )

    except Exception as e:
        # Erreur générique
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne: {str(e)}"
        )
```

---

## 🚦 Performance et Optimisation

### 1. Initialisation au Démarrage (IMPORTANT)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Singleton du pipeline RAG
rag_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialiser au démarrage, nettoyer à l'arrêt"""
    global rag_pipeline

    # Startup
    print("🚀 Chargement du modèle et des données...")
    rag_pipeline = get_rag_pipeline()
    rag_pipeline.load_data()
    print("✅ Prêt !")

    yield

    # Shutdown
    print("👋 Nettoyage...")

app = FastAPI(lifespan=lifespan)

# Les endpoints utilisent le rag_pipeline global
@app.post("/ask")
async def ask(req: QuestionRequest):
    result = generate_with_mode(
        rag_pipeline=rag_pipeline,  # ← Utilise l'instance globale
        ...
    )
    return result
```

### 2. Cache des Résultats

```python
from functools import lru_cache
import hashlib

# Cache simple en mémoire
@lru_cache(maxsize=100)
def get_cached_response(question: str, mode: str):
    """Cache les réponses pour les questions fréquentes"""
    result = generate_with_mode(
        rag_pipeline=rag_pipeline,
        question=question,
        mode=MODE_MAP[mode],
        stream=False
    )
    return result['response']

# Utilisation
response = get_cached_response(
    question="Quels sont mes meilleurs posts ?",
    mode="content_analyst"
)
```

### 3. Réglage des Paramètres

```python
# Pour des réponses RAPIDES mais moins détaillées
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question=question,
    mode=mode,
    n_results=3,        # Moins de posts = plus rapide
    max_tokens=500,     # Réponse plus courte
    temperature=0.3     # Moins créatif mais plus rapide
)

# Pour des réponses DÉTAILLÉES mais plus lentes
result = generate_with_mode(
    rag_pipeline=rag_pipeline,
    question=question,
    mode=mode,
    n_results=10,       # Plus de contexte
    max_tokens=2000,    # Réponse longue
    temperature=0.7     # Plus créatif
)
```

---

## 🧪 Tests

### Test Unitaire

```python
import pytest
from agent_modes import generate_with_mode, AgentMode
from rag_pipeline import get_rag_pipeline

@pytest.fixture(scope="module")
def rag():
    """Initialiser le pipeline une fois pour tous les tests"""
    pipeline = get_rag_pipeline()
    pipeline.load_data()
    return pipeline

def test_content_analyst_mode(rag):
    """Test du mode analyse de contenu"""
    result = generate_with_mode(
        rag_pipeline=rag,
        question="Quels sont mes meilleurs posts ?",
        mode=AgentMode.CONTENT_ANALYST,
        stream=False
    )

    assert 'response' in result
    assert isinstance(result['response'], str)
    assert len(result['response']) > 0
    assert result['mode'] == 'content_analyst'

def test_monetization_mode(rag):
    """Test du mode monétisation"""
    result = generate_with_mode(
        rag_pipeline=rag,
        question="Combien facturer ?",
        mode=AgentMode.MONETIZATION,
        stream=False
    )

    assert 'response' in result
    assert result['mode'] == 'monetization'

def test_streaming(rag):
    """Test du streaming"""
    result = generate_with_mode(
        rag_pipeline=rag,
        question="Test streaming",
        mode=AgentMode.CONTENT_ANALYST,
        stream=True
    )

    assert 'response_stream' in result

    # Consommer le stream
    chunks = list(result['response_stream'])
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
```

### Test d'Intégration API

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ask_endpoint():
    response = client.post("/ask", json={
        "question": "Quels sont mes meilleurs posts ?",
        "mode": "content_analyst",
        "n_posts": 3
    })

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["mode"] == "content_analyst"

def test_invalid_mode():
    response = client.post("/ask", json={
        "question": "Test",
        "mode": "invalid_mode"
    })

    assert response.status_code == 400
```

---

## 📊 Monitoring et Logs

```python
import logging
import time

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/ask")
async def ask(req: QuestionRequest):
    start_time = time.time()

    logger.info(f"📥 Requête reçue - Mode: {req.mode}, Question: {req.question[:50]}...")

    try:
        result = generate_with_mode(...)

        duration = time.time() - start_time
        logger.info(f"✅ Réponse générée en {duration:.2f}s - Mode: {req.mode}")

        return result

    except Exception as e:
        logger.error(f"❌ Erreur - Mode: {req.mode}, Erreur: {str(e)}")
        raise
```

---

## 🔑 Points Clés à Retenir

1. **Initialisation :** Charger le RAG pipeline UNE SEULE FOIS au démarrage
2. **Modes :** 4 modes disponibles (content_analyst, monetization, strategy, audience)
3. **Streaming :** Utiliser `stream=True` pour une meilleure UX
4. **Performance :** Ajuster `n_results`, `max_tokens` selon le besoin
5. **Fonction recommandée :** `generate_with_mode()` pour le backend

---

## 📞 Support

- **Documentation complète :** `MODES_GUIDE.md`
- **Exemples d'utilisation :** `USAGE_MODES.md`
- **Architecture :** `INTEGRATION_PROMPTS.md`

---

**Bon développement ! 🚀**