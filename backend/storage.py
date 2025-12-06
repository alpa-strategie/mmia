"""Stockage basé sur JSON pour les conversations."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .config import DATA_DIR


def ensure_data_dir():
    """S'assure que le répertoire de données existe."""
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


def get_conversation_path(conversation_id: str) -> str:
    """Obtient le chemin du fichier pour une conversation."""
    return os.path.join(DATA_DIR, f"{conversation_id}.json")


def create_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Crée une nouvelle conversation.

    Args:
        conversation_id: Identifiant unique pour la conversation

    Returns:
        Nouveau dict de conversation
    """
    ensure_data_dir()

    conversation = {
        "id": conversation_id,
        "created_at": datetime.utcnow().isoformat(),
        "title": "Nouvelle conversation",
        "messages": []
    }

    # Sauvegarder dans le fichier
    path = get_conversation_path(conversation_id)
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=2)

    return conversation


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Charge une conversation depuis le stockage.

    Args:
        conversation_id: Identifiant unique pour la conversation

    Returns:
        Dict de conversation ou None si non trouvé
    """
    path = get_conversation_path(conversation_id)

    if not os.path.exists(path):
        return None

    with open(path, 'r') as f:
        return json.load(f)


def save_conversation(conversation: Dict[str, Any]):
    """
    Sauvegarde une conversation dans le stockage.

    Args:
        conversation: Dict de conversation à sauvegarder
    """
    ensure_data_dir()

    path = get_conversation_path(conversation['id'])
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=2)


def list_conversations() -> List[Dict[str, Any]]:
    """
    Liste toutes les conversations (métadonnées uniquement).

    Returns:
        Liste de dicts de métadonnées de conversation
    """
    ensure_data_dir()

    conversations = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            path = os.path.join(DATA_DIR, filename)
            with open(path, 'r') as f:
                data = json.load(f)
                # Retourner uniquement les métadonnées
                conversations.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "title": data.get("title", "Nouvelle conversation"),
                    "message_count": len(data["messages"])
                })

    # Trier par date de création, plus récent en premier
    conversations.sort(key=lambda x: x["created_at"], reverse=True)

    return conversations


def add_user_message(conversation_id: str, content: str):
    """
    Ajoute un message utilisateur à une conversation.

    Args:
        conversation_id: Identifiant de conversation
        content: Contenu du message utilisateur
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} non trouvée")

    conversation["messages"].append({
        "role": "user",
        "content": content
    })

    save_conversation(conversation)


def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage3: Dict[str, Any]
):
    """
    Ajoute un message assistant avec les 3 étapes à une conversation.

    Args:
        conversation_id: Identifiant de conversation
        stage1: Liste des réponses individuelles des modèles
        stage2: Liste des classements des modèles
        stage3: Réponse finale synthétisée
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} non trouvée")

    conversation["messages"].append({
        "role": "assistant",
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3
    })

    save_conversation(conversation)


def update_conversation_title(conversation_id: str, title: str):
    """
    Met à jour le titre d'une conversation.

    Args:
        conversation_id: Identifiant de conversation
        title: Nouveau titre pour la conversation
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} non trouvée")

    conversation["title"] = title
    save_conversation(conversation)
