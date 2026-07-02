#!/bin/bash
echo "Demarrage du bot OPTC..."
echo ""

echo "Demarrage de Redis..."
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes
    sleep 2
    echo "Redis demarre."
else
    echo "Redis non trouve - le bot fonctionnera sans file de taches."
    echo "Installe Redis avec: sudo apt install redis-server (Linux)"
    echo "ou: brew install redis (Mac)"
fi
echo ""

echo "Demarrage de Celery Worker..."
celery -A celery_app worker --loglevel=info &
CELERY_PID=$!
sleep 2
echo "Celery Worker demarre (PID: $CELERY_PID)."
echo ""

echo "Demarrage de Flask..."
echo "Dashboard disponible sur: http://localhost:5000"
echo ""
python3 app.py

# Cleanup on exit
kill $CELERY_PID 2>/dev/null
