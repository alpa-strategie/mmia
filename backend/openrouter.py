"""Client API OpenRouter pour effectuer des requêtes LLM."""

import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Interroge un seul modèle via l'API OpenRouter.

    Args:
        model: Identifiant de modèle OpenRouter (ex: "openai/gpt-4o")
        messages: Liste de dicts de messages avec 'role' et 'content'
        timeout: Délai d'expiration de la requête en secondes

    Returns:
        Dict de réponse avec 'content' et optionnellement 'reasoning_details', ou None si échec
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Erreur lors de l'interrogation du modèle {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Interroge plusieurs modèles en parallèle.

    Args:
        models: Liste des identifiants de modèles OpenRouter
        messages: Liste de dicts de messages à envoyer à chaque modèle

    Returns:
        Dict mappant l'identifiant du modèle au dict de réponse (ou None si échec)
    """
    import asyncio

    # Créer des tâches pour tous les modèles
    tasks = [query_model(model, messages) for model in models]

    # Attendre que tous se terminent
    responses = await asyncio.gather(*tasks)

    # Mapper les modèles à leurs réponses
    return {model: response for model, response in zip(models, responses)}
