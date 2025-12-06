# MMiA (Mes Mentors IA)

![mmia](header.jpg)

L'idée de ce mini projet est qu'au lieu de poser une question à votre fournisseur de LLM préféré (par exemple OpenAI GPT 5.1, Google Gemini 3.0 Pro, Anthropic Claude Sonnet 4.5, xAI Grok 4, etc.), vous pouvez les regrouper dans votre "Conseil de Mentors IA". C'est une simple application web locale qui ressemble essentiellement à ChatGPT, sauf qu'elle utilise OpenRouter pour envoyer votre requête à plusieurs LLMs, il leur est ensuite demandé d'examiner et de classer le travail de chacun, et enfin un LLM Président produit la réponse finale.

**IMPORTANT** Il faut se créer un compte sur OpenRouter (https://openrouter.ai/) et mettre au minimum 5 US$ de crédit

En plus de détails, voici ce qui se passe lorsque vous soumettez une requête :

1. **Étape 1 : Premières opinions**. La requête de l'utilisateur est donnée à tous les LLMs individuellement, et les réponses sont collectées. Les réponses individuelles sont affichées dans une "vue par onglets", afin que l'utilisateur puisse les inspecter une par une.
2. **Étape 2 : Revue**. Chaque LLM individuel reçoit les réponses des autres LLMs. En coulisse, les identités des LLMs sont anonymisées afin que le LLM ne puisse pas favoriser certains lors de l'évaluation de leurs productions. Le LLM est invité à les classer en termes de précision et de perspicacité.
3. **Étape 3 : Réponse finale**. Le Président désigné du Conseil des Mentors IA prend toutes les réponses des modèles et les compile en une seule réponse finale qui est présentée à l'utilisateur.

## Alerte Code Vibe

Ce projet a été codé à 99% en mode vibe comme un hack amusant du soir parce que je voulais explorer et évaluer un certain nombre de LLMs. C'est agréable et utile de voir plusieurs réponses côte à côte, ainsi que les opinions croisées de tous les LLMs sur les sorties des uns et des autres. Je n'est pas l'intention pas le supporter de quelque manière que ce soit, il est fourni ici tel quel pour l'inspiration d'autres personnes.

## Installation

### 0. Télécharger ce git repo
Par ligne de commande en HTTPS
ou
Simplement télécharger le ZIP

Par ligne de commande allez ensuite dans le bon répertoire.

### 1. Installer les dépendances

Le projet utilise [uv](https://docs.astral.sh/uv/) pour la gestion du projet.

**Backend :**
```bash
uv sync
```

**Frontend :**
```bash
cd frontend
npm install
cd ..
```

### 2. Configurer la clé API

Créez un fichier `.env.local` à la racine du projet :

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

Obtenez votre clé API sur [openrouter.ai](https://openrouter.ai/settings/keys). Assurez-vous d'acheter les crédits dont vous avez besoin.

### 3. Configurer les modèles (Optionnel)

Modifiez `backend/config.py` pour personnaliser le conseil :
Configuration actuelle:
- openai/gpt-5.1 : # The Strategist
- google/gemini-3-pro-preview : # The Analyst (Massive Context)
- anthropic/claude-sonnet-4.5 : # The Writer/Nuance Specialist
- x-ai/grok-4 : # The Critic (No Guardrails)

```python
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "xai/grok-4-mini",
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
```

## Lancer l'application

**Option 1 : Utiliser le script de démarrage**
```bash
./start.sh
```

**Option 2 : Lancer manuellement**

Terminal 1 (Backend) :
```bash
uv run python -m backend.main
```

Terminal 2 (Frontend) :
```bash
cd frontend
npm run dev
```

Puis ouvrez http://localhost:5173 dans votre navigateur.

## Stack technique

- **Backend :** FastAPI (Python 3.10+), async httpx, API OpenRouter
- **Frontend :** React + Vite, react-markdown pour le rendu
- **Stockage :** Fichiers JSON dans `data/conversations/`
- **Gestion des paquets :** uv pour Python, npm pour JavaScript
