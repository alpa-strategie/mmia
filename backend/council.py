"""Orchestration du conseil de mentors IA en 3 étapes."""

from typing import List, Dict, Any, Tuple
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Étape 1 : Collecte les réponses individuelles de tous les modèles du conseil.

    Args:
        user_query: La question de l'utilisateur

    Returns:
        Liste de dicts avec les clés 'model' et 'response'
    """
    messages = [{"role": "user", "content": user_query}]

    # Interroger tous les modèles en parallèle
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Formater les résultats
    stage1_results = []
    for model, response in responses.items():
        if response is not None:  # Inclure uniquement les réponses réussies
            stage1_results.append({
                "model": model,
                "response": response.get('content', '')
            })

    return stage1_results


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Étape 2 : Chaque modèle classe les réponses anonymisées.

    Args:
        user_query: La requête utilisateur originale
        stage1_results: Résultats de l'Étape 1

    Returns:
        Tuple de (liste de classements, mappage label_to_model)
    """
    # Créer des étiquettes anonymisées pour les réponses (Réponse A, Réponse B, etc.)
    labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...

    # Créer un mappage de l'étiquette au nom du modèle
    label_to_model = {
        f"Réponse {label}": result['model']
        for label, result in zip(labels, stage1_results)
    }

    # Construire le prompt de classement
    responses_text = "\n\n".join([
        f"Réponse {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""Vous évaluez différentes réponses à la question suivante :

Question : {user_query}

Voici les réponses de différents modèles (anonymisées) :

{responses_text}

Votre tâche :
1. D'abord, évaluez chaque réponse individuellement. Pour chaque réponse, expliquez ce qu'elle fait bien et ce qu'elle fait mal.
2. Ensuite, à la toute fin de votre réponse, fournissez un classement final.

IMPORTANT : Votre classement final DOIT être formaté EXACTEMENT comme suit :
- Commencez par la ligne "CLASSEMENT FINAL :" (en majuscules, avec deux-points)
- Ensuite, listez les réponses de la meilleure à la pire sous forme de liste numérotée
- Chaque ligne doit être : numéro, point, espace, puis UNIQUEMENT l'étiquette de réponse (ex: "1. Réponse A")
- N'ajoutez aucun autre texte ou explication dans la section de classement

Exemple du format correct pour votre réponse COMPLÈTE :

La Réponse A fournit de bons détails sur X mais manque Y...
La Réponse B est précise mais manque de profondeur sur Z...
La Réponse C offre la réponse la plus complète...

CLASSEMENT FINAL :
1. Réponse C
2. Réponse A
3. Réponse B

Maintenant, fournissez votre évaluation et classement :"""

    messages = [{"role": "user", "content": ranking_prompt}]

    # Obtenir les classements de tous les modèles du conseil en parallèle
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Formater les résultats
    stage2_results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get('content', '')
            parsed = parse_ranking_from_text(full_text)
            stage2_results.append({
                "model": model,
                "ranking": full_text,
                "parsed_ranking": parsed
            })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Étape 3 : Le président synthétise la réponse finale.

    Args:
        user_query: La requête utilisateur originale
        stage1_results: Réponses individuelles des modèles de l'Étape 1
        stage2_results: Classements de l'Étape 2

    Returns:
        Dict avec les clés 'model' et 'response'
    """
    # Construire un contexte complet pour le président
    stage1_text = "\n\n".join([
        f"Modèle : {result['model']}\nRéponse : {result['response']}"
        for result in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"Modèle : {result['model']}\nClassement : {result['ranking']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""Vous êtes le Président d'un Conseil de Mentors IA. Plusieurs modèles d'IA ont fourni des réponses à la question d'un utilisateur, puis ont classé les réponses des uns et des autres.

Question originale : {user_query}

ÉTAPE 1 - Réponses individuelles :
{stage1_text}

ÉTAPE 2 - Classements par les pairs :
{stage2_text}

Votre tâche en tant que Président est de synthétiser toutes ces informations en une seule réponse complète et précise à la question originale de l'utilisateur. Tenez compte de :
- Les réponses individuelles et leurs perspectives
- Les classements par les pairs et ce qu'ils révèlent sur la qualité des réponses
- Tous les schémas d'accord ou de désaccord

Fournissez une réponse finale claire et bien argumentée qui représente la sagesse collective du conseil :"""

    messages = [{"role": "user", "content": chairman_prompt}]

    # Interroger le modèle président
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        # Solution de repli si le président échoue
        return {
            "model": CHAIRMAN_MODEL,
            "response": "Erreur : Impossible de générer la synthèse finale."
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get('content', '')
    }


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """
    Analyse la section CLASSEMENT FINAL du texte de réponse du modèle.

    Args:
        ranking_text: Le texte de réponse complet du modèle

    Returns:
        Liste des étiquettes de réponse dans l'ordre classé
    """
    import re

    # Chercher la section "CLASSEMENT FINAL :"
    if "CLASSEMENT FINAL :" in ranking_text or "CLASSEMENT FINAL:" in ranking_text:
        # Extraire tout après "CLASSEMENT FINAL :"
        parts = ranking_text.split("CLASSEMENT FINAL")
        if len(parts) >= 2:
            ranking_section = parts[1]
            # Essayer d'extraire le format de liste numérotée (ex: "1. Réponse A")
            # Ce motif recherche : numéro, point, espace optionnel, "Réponse X"
            numbered_matches = re.findall(r'\d+\.\s*Réponse [A-Z]', ranking_section)
            if numbered_matches:
                # Extraire juste la partie "Réponse X"
                return [re.search(r'Réponse [A-Z]', m).group() for m in numbered_matches]

            # Solution de repli : Extraire tous les motifs "Réponse X" dans l'ordre
            matches = re.findall(r'Réponse [A-Z]', ranking_section)
            return matches

    # Solution de repli : essayer de trouver n'importe quel motif "Réponse X" dans l'ordre
    matches = re.findall(r'Réponse [A-Z]', ranking_text)
    return matches


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Calcule les classements agrégés à travers tous les modèles.

    Args:
        stage2_results: Classements de chaque modèle
        label_to_model: Mappage des étiquettes anonymes aux noms de modèles

    Returns:
        Liste de dicts avec le nom du modèle et le rang moyen, triés du meilleur au pire
    """
    from collections import defaultdict

    # Suivre les positions pour chaque modèle
    model_positions = defaultdict(list)

    for ranking in stage2_results:
        ranking_text = ranking['ranking']

        # Analyser le classement à partir du format structuré
        parsed_ranking = parse_ranking_from_text(ranking_text)

        for position, label in enumerate(parsed_ranking, start=1):
            if label in label_to_model:
                model_name = label_to_model[label]
                model_positions[model_name].append(position)

    # Calculer la position moyenne pour chaque modèle
    aggregate = []
    for model, positions in model_positions.items():
        if positions:
            avg_rank = sum(positions) / len(positions)
            aggregate.append({
                "model": model,
                "average_rank": round(avg_rank, 2),
                "rankings_count": len(positions)
            })

    # Trier par rang moyen (plus bas est meilleur)
    aggregate.sort(key=lambda x: x['average_rank'])

    return aggregate


async def generate_conversation_title(user_query: str) -> str:
    """
    Génère un titre court pour une conversation basé sur le premier message de l'utilisateur.

    Args:
        user_query: Le premier message de l'utilisateur

    Returns:
        Un titre court (3-5 mots)
    """
    title_prompt = f"""Générez un titre très court (3-5 mots maximum) qui résume la question suivante.
Le titre doit être concis et descriptif. N'utilisez pas de guillemets ou de ponctuation dans le titre.

Question : {user_query}

Titre :"""

    messages = [{"role": "user", "content": title_prompt}]

    # Utiliser gemini-2.5-flash pour la génération de titre (rapide et économique)
    response = await query_model("google/gemini-2.5-flash", messages, timeout=30.0)

    if response is None:
        # Solution de repli vers un titre générique
        return "Nouvelle conversation"

    title = response.get('content', 'Nouvelle conversation').strip()

    # Nettoyer le titre - supprimer les guillemets, limiter la longueur
    title = title.strip('"\'')

    # Tronquer si trop long
    if len(title) > 50:
        title = title[:47] + "..."

    return title


async def run_full_council(user_query: str) -> Tuple[List, List, Dict, Dict]:
    """
    Exécute le processus complet du conseil en 3 étapes.

    Args:
        user_query: La question de l'utilisateur

    Returns:
        Tuple de (stage1_results, stage2_results, stage3_result, metadata)
    """
    # Étape 1 : Collecter les réponses individuelles
    stage1_results = await stage1_collect_responses(user_query)

    # Si aucun modèle n'a répondu avec succès, retourner une erreur
    if not stage1_results:
        return [], [], {
            "model": "error",
            "response": "Tous les modèles ont échoué à répondre. Veuillez réessayer."
        }, {}

    # Étape 2 : Collecter les classements
    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)

    # Calculer les classements agrégés
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    # Étape 3 : Synthétiser la réponse finale
    stage3_result = await stage3_synthesize_final(
        user_query,
        stage1_results,
        stage2_results
    )

    # Préparer les métadonnées
    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings
    }

    return stage1_results, stage2_results, stage3_result, metadata
