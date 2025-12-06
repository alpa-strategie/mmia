"""Configuration pour MMiA (Mes Mentors IA)."""

import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# Clé API OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Membres du conseil - liste des identifiants de modèles OpenRouter
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "xai/grok-4-mini",
]

# Modèle président - synthétise la réponse finale
CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

# Point de terminaison API OpenRouter
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Répertoire de données pour le stockage des conversations
DATA_DIR = "data/conversations"
