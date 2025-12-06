# MMiA (Mes Mentors IA)

![mmia](header.jpg)

L'idée de ce dépôt est qu'au lieu de poser une question à votre fournisseur de LLM préféré (par exemple OpenAI GPT 5.1, Google Gemini 3.0 Pro, Anthropic Claude Sonnet 4.5, xAI Grok 4, etc.), vous pouvez les regrouper dans votre "Conseil de Mentors IA". Ce dépôt est une simple application web locale qui ressemble essentiellement à ChatGPT, sauf qu'elle utilise OpenRouter pour envoyer votre requête à plusieurs LLMs, leur demande ensuite d'examiner et de classer le travail de chacun, et enfin un LLM Président produit la réponse finale.

En un peu plus de détails, voici ce qui se passe lorsque vous soumettez une requête :

1. **Étape 1 : Premières opinions**. La requête de l'utilisateur est donnée à tous les LLMs individuellement, et les réponses sont collectées. Les réponses individuelles sont affichées dans une "vue par onglets", afin que l'utilisateur puisse les inspecter une par une.
2. **Étape 2 : Revue**. Chaque LLM individuel reçoit les réponses des autres LLMs. En coulisse, les identités des LLMs sont anonymisées afin que le LLM ne puisse pas favoriser certains lors de l'évaluation de leurs productions. Le LLM est invité à les classer en termes de précision et de perspicacité.
3. **Étape 3 : Réponse finale**. Le Président désigné du Conseil des Mentors IA prend toutes les réponses des modèles et les compile en une seule réponse finale qui est présentée à l'utilisateur.

## Alerte Code Vibe

Ce projet a été codé à 99% en mode vibe comme un hack amusant du samedi parce que je voulais explorer et évaluer un certain nombre de LLMs côte à côte dans le processus de [lecture de livres avec les LLMs](https://x.com/karpathy/status/1990577951671509438). C'est agréable et utile de voir plusieurs réponses côte à côte, ainsi que les opinions croisées de tous les LLMs sur les sorties des uns et des autres. Je ne vais pas le supporter de quelque manière que ce soit, il est fourni ici tel quel pour l'inspiration d'autres personnes et je n'ai pas l'intention de l'améliorer. Le code est éphémère maintenant et les bibliothèques sont dépassées, demandez à votre LLM de le modifier de la manière que vous souhaitez.

## Installation

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

Obtenez votre clé API sur [openrouter.ai](https://openrouter.ai/). Assurez-vous d'acheter les crédits dont vous avez besoin, ou inscrivez-vous pour un rechargement automatique.

### 3. Configurer les modèles (Optionnel)

Modifiez `backend/config.py` pour personnaliser le conseil :

```python
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "mistralai/mistral-large-2512",
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
