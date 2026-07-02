#!/bin/bash
echo "=============================="
echo "  OPTC Bot - Démarrage"
echo "=============================="
echo ""

# Démarrer Redis en arrière-plan (si disponible)
if command -v redis-server &>/dev/null; then
    redis-server --daemonize yes >/dev/null 2>&1
    echo "[OK] Redis démarré"
else
    echo "[INFO] Redis non trouvé - utilisation du mode sans Redis"
fi
echo ""

# Démarrer Celery Worker dans un nouveau terminal
echo "Démarrage du worker Celery..."
if command -v gnome-terminal &>/dev/null; then
    gnome-terminal -- bash -c "celery -A celery_app worker --loglevel=info; read" &
elif command -v osascript &>/dev/null; then
    # macOS
    osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"' && celery -A celery_app worker --loglevel=info"' &
else
    # Fallback: arrière-plan
    celery -A celery_app worker --loglevel=info &
fi

# Pause pour laisser Celery démarrer
sleep 2

# Ouvrir le navigateur
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:5000 &
elif command -v open &>/dev/null; then
    open http://localhost:5000 &
fi

echo "=============================="
echo "  Bot démarré!"
echo "  Ouvre: http://localhost:5000"
echo "=============================="
echo ""

# Lancer Flask
python3 app.py
