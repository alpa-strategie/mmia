#!/bin/bash

# MMiA (Mes Mentors IA) - Script de démarrage

echo "Démarrage de MMiA..."
echo ""

# Démarrer le backend
echo "Démarrage du backend sur http://localhost:8001..."
uv run python -m backend.main &
BACKEND_PID=$!

# Attendre un peu que le backend démarre
sleep 2

# Démarrer le frontend
echo "Démarrage du frontend sur http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ MMiA est en cours d'exécution !"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les deux serveurs"

# Attendre Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
