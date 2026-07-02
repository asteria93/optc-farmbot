#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${TMPDIR:-/tmp}/optc-farmbot"

mkdir -p "$LOG_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python est requis mais introuvable."
  exit 1
fi

cd "$REPO_ROOT"

if ! "$PYTHON_CMD" -c "import flask, celery, redis" >/dev/null 2>&1; then
  echo "Installation des dépendances..."
  "$PYTHON_CMD" -m pip install -r requirements.txt
fi

start_redis() {
  if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
    echo "Redis est déjà lancé."
    return
  fi

  if ! command -v redis-server >/dev/null 2>&1; then
    echo "redis-server est introuvable. Installe Redis puis relance le script."
    exit 1
  fi

  echo "Démarrage de Redis..."
  redis-server >"$LOG_DIR/redis.log" 2>&1 &
  sleep 3
}

start_celery() {
  echo "Démarrage du worker Celery..."
  "$PYTHON_CMD" -m celery -A celery_app:celery_app worker --loglevel=info >"$LOG_DIR/celery.log" 2>&1 &
}

open_browser() {
  if command -v xdg-open >/dev/null 2>&1; then
    (sleep 3 && xdg-open http://localhost:5000 >/dev/null 2>&1) &
  elif command -v open >/dev/null 2>&1; then
    (sleep 3 && open http://localhost:5000 >/dev/null 2>&1) &
  fi
}

start_redis
start_celery
open_browser

echo "Démarrage de Flask sur http://localhost:5000 ..."
"$PYTHON_CMD" app.py
