"""Backend FastAPI pour MMiA (Mes Mentors IA)."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import json
import asyncio

from . import storage
from .council import run_full_council, generate_conversation_title, stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final, calculate_aggregate_rankings

app = FastAPI(title="API MMiA (Mes Mentors IA)")

# Activer CORS pour le développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateConversationRequest(BaseModel):
    """Requête pour créer une nouvelle conversation."""
    pass


class SendMessageRequest(BaseModel):
    """Requête pour envoyer un message dans une conversation."""
    content: str


class ConversationMetadata(BaseModel):
    """Métadonnées de conversation pour la vue liste."""
    id: str
    created_at: str
    title: str
    message_count: int


class Conversation(BaseModel):
    """Conversation complète avec tous les messages."""
    id: str
    created_at: str
    title: str
    messages: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Point de terminaison de vérification de santé."""
    return {"status": "ok", "service": "API MMiA (Mes Mentors IA)"}


@app.get("/api/conversations", response_model=List[ConversationMetadata])
async def list_conversations():
    """Liste toutes les conversations (métadonnées uniquement)."""
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation)
async def create_conversation(request: CreateConversationRequest):
    """Crée une nouvelle conversation."""
    conversation_id = str(uuid.uuid4())
    conversation = storage.create_conversation(conversation_id)
    return conversation


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Obtient une conversation spécifique avec tous ses messages."""
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation


@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Envoie un message et exécute le processus du conseil en 3 étapes.
    Retourne la réponse complète avec toutes les étapes.
    """
    # Vérifier si la conversation existe
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")

    # Vérifier si c'est le premier message
    is_first_message = len(conversation["messages"]) == 0

    # Ajouter le message utilisateur
    storage.add_user_message(conversation_id, request.content)

    # Si c'est le premier message, générer un titre
    if is_first_message:
        title = await generate_conversation_title(request.content)
        storage.update_conversation_title(conversation_id, title)

    # Exécuter le processus du conseil en 3 étapes
    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(
        request.content
    )

    # Ajouter le message assistant avec toutes les étapes
    storage.add_assistant_message(
        conversation_id,
        stage1_results,
        stage2_results,
        stage3_result
    )

    # Retourner la réponse complète avec métadonnées
    return {
        "stage1": stage1_results,
        "stage2": stage2_results,
        "stage3": stage3_result,
        "metadata": metadata
    }


@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    """
    Envoie un message et diffuse le processus du conseil en 3 étapes.
    Retourne des événements Server-Sent Events au fur et à mesure que chaque étape se termine.
    """
    # Vérifier si la conversation existe
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")

    # Vérifier si c'est le premier message
    is_first_message = len(conversation["messages"]) == 0

    async def event_generator():
        try:
            # Ajouter le message utilisateur
            storage.add_user_message(conversation_id, request.content)

            # Démarrer la génération de titre en parallèle (ne pas attendre encore)
            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(generate_conversation_title(request.content))

            # Étape 1 : Collecter les réponses
            yield f"data: {json.dumps({'type': 'stage1_start'})}\n\n"
            stage1_results = await stage1_collect_responses(request.content)
            yield f"data: {json.dumps({'type': 'stage1_complete', 'data': stage1_results})}\n\n"

            # Étape 2 : Collecter les classements
            yield f"data: {json.dumps({'type': 'stage2_start'})}\n\n"
            stage2_results, label_to_model = await stage2_collect_rankings(request.content, stage1_results)
            aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)
            yield f"data: {json.dumps({'type': 'stage2_complete', 'data': stage2_results, 'metadata': {'label_to_model': label_to_model, 'aggregate_rankings': aggregate_rankings}})}\n\n"

            # Étape 3 : Synthétiser la réponse finale
            yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
            stage3_result = await stage3_synthesize_final(request.content, stage1_results, stage2_results)
            yield f"data: {json.dumps({'type': 'stage3_complete', 'data': stage3_result})}\n\n"

            # Attendre la génération de titre si elle a été démarrée
            if title_task:
                title = await title_task
                storage.update_conversation_title(conversation_id, title)
                yield f"data: {json.dumps({'type': 'title_complete', 'data': {'title': title}})}\n\n"

            # Sauvegarder le message assistant complet
            storage.add_assistant_message(
                conversation_id,
                stage1_results,
                stage2_results,
                stage3_result
            )

            # Envoyer l'événement de fin
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            # Envoyer un événement d'erreur
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
