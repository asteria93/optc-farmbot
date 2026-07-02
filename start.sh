#!/usr/bin/env bash
# OPTC Farming Bot — Linux/Mac start script
# Starts Redis (if not running), Celery worker, and Flask web server.
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "======================================"
echo "  OPTC Farming Bot — Starting"
echo "======================================"
echo ""

# --- Virtual environment ---
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run ./setup.sh first."
    exit 1
fi
# shellcheck disable=SC1091
source venv/bin/activate

# --- .env check ---
if [ ! -f ".env" ]; then
    echo "ERROR: .env not found. Run ./setup.sh first."
    exit 1
fi

# --- Redis ---
if command -v redis-cli &>/dev/null && redis-cli ping &>/dev/null 2>&1; then
    echo "✓ Redis already running"
else
    echo "Starting Redis..."
    if command -v redis-server &>/dev/null; then
        redis-server --daemonize yes
        sleep 1
        echo "✓ Redis started"
    else
        echo "⚠ redis-server not found — please start Redis manually."
    fi
fi

mkdir -p logs

# --- Celery worker ---
echo "Starting Celery worker..."
celery -A app.celery worker --loglevel=info \
    --logfile=logs/celery.log \
    --detach \
    --pidfile=logs/celery.pid 2>/dev/null || \
celery -A app.celery worker --loglevel=info &
CELERY_PID=$!
echo "✓ Celery worker started (pid: ${CELERY_PID:-background})"

# Give Celery a moment to connect
sleep 2

# --- Flask web server ---
echo "Starting Flask web server..."
echo ""
echo "======================================"
echo "  Dashboard: http://localhost:5000"
echo "  Press Ctrl+C to stop"
echo "======================================"
echo ""

python app.py
