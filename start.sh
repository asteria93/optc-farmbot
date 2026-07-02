#!/bin/bash
echo "Démarrage du bot OPTC..."
echo ""

echo "Démarrage de Redis..."
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes
    sleep 2
    echo "Redis démarré."
else
    echo "Redis non trouvé - le bot fonctionnera sans file de tâches."
    echo "Installe Redis avec: sudo apt install redis-server (Linux)"
    echo "ou: brew install redis (Mac)"
fi
echo ""

echo "Démarrage de Celery Worker..."
celery -A celery_app worker --loglevel=info &
CELERY_PID=$!
sleep 2
echo "Celery Worker démarré (PID: $CELERY_PID)."
echo ""

echo "Démarrage de Flask..."
echo "Dashboard disponible sur: http://localhost:5000"
echo ""
python3 app.py

# Cleanup on exit
kill $CELERY_PID 2>/dev/null
