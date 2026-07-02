#!/bin/bash
echo "=============================="
echo "  OPTC Bot - Demarrage"
echo "=============================="
echo ""

# Demarrer Redis en arriere-plan (si disponible)
if command -v redis-server &>/dev/null; then
    redis-server --daemonize yes >/dev/null 2>&1
    echo "[OK] Redis demarre"
else
    echo "[INFO] Redis non trouve - utilisation du mode sans Redis"
fi
echo ""

# Demarrer Celery Worker dans un nouveau terminal
echo "Demarrage du worker Celery..."
if command -v gnome-terminal &>/dev/null; then
    gnome-terminal -- bash -c "celery -A celery_app worker --loglevel=info; read" &
elif command -v osascript &>/dev/null; then
    # macOS
    osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"' && celery -A celery_app worker --loglevel=info"' &
else
    # Fallback: arriere-plan
    celery -A celery_app worker --loglevel=info &
fi

# Pause pour laisser Celery demarrer
sleep 2

# Ouvrir le navigateur
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:5000 &
elif command -v open &>/dev/null; then
    open http://localhost:5000 &
fi

echo "=============================="
echo "  Bot demarre!"
echo "  Ouvre: http://localhost:5000"
echo "=============================="
echo ""

# Lancer Flask
python3 app.py
