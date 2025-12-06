# CLAUDE.md - Notes techniques pour MMiA (Mes Mentors IA)

Ce fichier contient des détails techniques, des décisions architecturales et des notes d'implémentation importantes pour les futures sessions de développement.

## Vue d'ensemble du projet

MMiA (Mes Mentors IA) est un système de délibération en 3 étapes où plusieurs LLMs répondent collaborativement aux questions des utilisateurs. L'innovation clé est l'examen par les pairs anonymisé à l'étape 2, empêchant les modèles de favoriser certains.

## Architecture

### Structure du Backend (`backend/`)

**`config.py`**
- Contient `COUNCIL_MODELS` (liste des identifiants de modèles OpenRouter)
- Contient `CHAIRMAN_MODEL` (modèle qui synthétise la réponse finale)
- Utilise la variable d'environnement `OPENROUTER_API_KEY` depuis `.env.local`
- Le backend fonctionne sur le **port 8001** (PAS 8000 - l'utilisateur avait une autre application sur 8000)

**`openrouter.py`**
- `query_model()` : Requête de modèle unique asynchrone
- `query_models_parallel()` : Requêtes parallèles utilisant `asyncio.gather()`
- Retourne un dict avec 'content' et optionnellement 'reasoning_details'
- Dégradation gracieuse : retourne None en cas d'échec, continue avec les réponses réussies

**`council.py`** - La logique centrale
- `stage1_collect_responses()` : Requêtes parallèles à tous les modèles du conseil
- `stage2_collect_rankings()` :
  - Anonymise les réponses en "Response A, B, C, etc."
  - Crée un mappage `label_to_model` pour la dé-anonymisation
  - Invite les modèles à évaluer et classer (avec des exigences de format strictes)
  - Retourne un tuple : (rankings_list, label_to_model_dict)
  - Chaque classement inclut à la fois le texte brut et la liste `parsed_ranking`
- `stage3_synthesize_final()` : Le président synthétise à partir de toutes les réponses + classements
- `parse_ranking_from_text()` : Extrait la section "FINAL RANKING:", gère à la fois les listes numérotées et le format simple
- `calculate_aggregate_rankings()` : Calcule la position de classement moyenne à travers toutes les évaluations par les pairs

**`storage.py`**
- Stockage de conversation basé sur JSON dans `data/conversations/`
- Chaque conversation : `{id, created_at, messages[]}`
- Les messages de l'assistant contiennent : `{role, stage1, stage2, stage3}`
- Note : les métadonnées (label_to_model, aggregate_rankings) ne sont PAS persistées dans le stockage, seulement retournées via l'API

**`main.py`**
- Application FastAPI avec CORS activé pour localhost:5173 et localhost:3000
- POST `/api/conversations/{id}/message` retourne des métadonnées en plus des étapes
- Les métadonnées incluent : mappage label_to_model et aggregate_rankings

### Structure du Frontend (`frontend/src/`)

**`App.jsx`**
- Orchestration principale : gère la liste des conversations et la conversation actuelle
- Gère l'envoi de messages et le stockage des métadonnées
- Important : les métadonnées sont stockées dans l'état de l'interface pour l'affichage mais ne sont pas persistées dans le JSON du backend

**`components/ChatInterface.jsx`**
- Zone de texte multiligne (3 lignes, redimensionnable)
- Entrée pour envoyer, Maj+Entrée pour nouvelle ligne
- Messages utilisateur enveloppés dans la classe markdown-content pour le rembourrage

**`components/Stage1.jsx`**
- Vue par onglets des réponses individuelles des modèles
- Rendu ReactMarkdown avec enveloppe markdown-content

**`components/Stage2.jsx`**
- **Fonctionnalité critique** : Vue par onglets montrant le texte d'évaluation BRUT de chaque modèle
- La dé-anonymisation se produit CÔTÉ CLIENT pour l'affichage (les modèles reçoivent des étiquettes anonymes)
- Affiche "Classement extrait" sous chaque évaluation pour que les utilisateurs puissent valider l'analyse
- Les classements agrégés sont affichés avec la position moyenne et le nombre de votes
- Le texte explicatif clarifie que les noms de modèles en gras sont uniquement pour la lisibilité

**`components/Stage3.jsx`**
- Réponse finale synthétisée par le président
- Arrière-plan teinté de vert (#f0fff0) pour mettre en évidence la conclusion

**Styles (`*.css`)**
- Thème en mode clair (pas de mode sombre)
- Couleur principale : #4a90e2 (bleu)
- Style markdown global dans `index.css` avec la classe `.markdown-content`
- Rembourrage de 12px sur tout le contenu markdown pour éviter l'apparence encombrée

## Décisions de conception clés

### Format du prompt de l'étape 2
Le prompt de l'étape 2 est très spécifique pour garantir une sortie analysable :
```
1. Évaluer chaque réponse individuellement d'abord
2. Fournir un en-tête "FINAL RANKING:"
3. Format de liste numérotée : "1. Response C", "2. Response A", etc.
4. Pas de texte supplémentaire après la section de classement
```

Ce format strict permet une analyse fiable tout en obtenant des évaluations réfléchies.

### Stratégie de dé-anonymisation
- Les modèles reçoivent : "Response A", "Response B", etc.
- Le backend crée un mappage : `{"Response A": "openai/gpt-5.1", ...}`
- Le frontend affiche les noms de modèles en **gras** pour la lisibilité
- Les utilisateurs voient une explication que l'évaluation originale utilisait des étiquettes anonymes
- Cela évite les biais tout en maintenant la transparence

### Philosophie de gestion des erreurs
- Continuer avec les réponses réussies si certains modèles échouent (dégradation gracieuse)
- Ne jamais faire échouer la requête entière en raison de l'échec d'un seul modèle
- Journaliser les erreurs mais ne pas les exposer à l'utilisateur sauf si tous les modèles échouent

### Transparence UI/UX
- Toutes les sorties brutes sont inspectables via des onglets
- Les classements analysés sont affichés sous le texte brut pour validation
- Les utilisateurs peuvent vérifier l'interprétation du système des sorties du modèle
- Cela renforce la confiance et permet le débogage des cas limites

## Détails d'implémentation importants

### Imports relatifs
Tous les modules backend utilisent des imports relatifs (par exemple, `from .config import ...`) et non des imports absolus. C'est crucial pour que le système de modules de Python fonctionne correctement lors de l'exécution avec `python -m backend.main`.

### Configuration des ports
- Backend : 8001 (changé de 8000 pour éviter les conflits)
- Frontend : 5173 (par défaut Vite)
- Mettre à jour à la fois `backend/main.py` et `frontend/src/api.js` en cas de changement

### Rendu Markdown
Tous les composants ReactMarkdown doivent être enveloppés dans `<div className="markdown-content">` pour un espacement approprié. Cette classe est définie globalement dans `index.css`.

### Configuration des modèles
Les modèles sont codés en dur dans `backend/config.py`. Le président peut être le même ou différent des membres du conseil. La valeur par défaut actuelle est Gemini comme président selon la préférence de l'utilisateur.

## Pièges courants

1. **Erreurs d'import de module** : Toujours exécuter le backend avec `python -m backend.main` depuis la racine du projet, pas depuis le répertoire backend
2. **Problèmes CORS** : Le frontend doit correspondre aux origines autorisées dans le middleware CORS de `main.py`
3. **Échecs d'analyse de classement** : Si les modèles ne suivent pas le format, une regex de secours extrait tous les motifs "Response X" dans l'ordre
4. **Métadonnées manquantes** : Les métadonnées sont éphémères (non persistées), disponibles uniquement dans les réponses API

## Idées d'améliorations futures

- Conseil/président configurable via l'interface au lieu du fichier de configuration
- Réponses en streaming au lieu du chargement par lots
- Exporter les conversations vers markdown/PDF
- Analyses de performances des modèles au fil du temps
- Critères de classement personnalisés (pas seulement précision/perspicacité)
- Support pour les modèles de raisonnement (o1, etc.) avec une gestion spéciale

## Notes de test

Utilisez `test_openrouter.py` pour vérifier la connectivité de l'API et tester différents identifiants de modèles avant de les ajouter au conseil. Le script teste à la fois les modes streaming et non-streaming.

## Résumé du flux de données

```
Requête utilisateur
    ↓
Étape 1 : Requêtes parallèles → [réponses individuelles]
    ↓
Étape 2 : Anonymiser → Requêtes de classement parallèles → [évaluations + classements analysés]
    ↓
Calcul des classements agrégés → [triés par position moyenne]
    ↓
Étape 3 : Synthèse par le président avec contexte complet
    ↓
Retour : {stage1, stage2, stage3, metadata}
    ↓
Frontend : Affichage avec onglets + interface de validation
```

L'ensemble du flux est asynchrone/parallèle lorsque c'est possible pour minimiser la latence.
