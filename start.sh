#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs .run

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python n'est pas installé."
  exit 1
fi

if ! command -v redis-server >/dev/null 2>&1; then
  echo "redis-server est introuvable."
  exit 1
fi

if ! command -v celery >/dev/null 2>&1; then
  echo "celery est introuvable."
  exit 1
fi

nohup redis-server > logs/redis.log 2>&1 &
echo $! > .run/redis.pid

nohup celery -A celery_app worker --loglevel=info > logs/celery.log 2>&1 &
echo $! > .run/celery.pid

nohup "$PYTHON_CMD" app.py > logs/flask.log 2>&1 &
echo $! > .run/flask.pid

sleep 3

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:5000 >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open http://localhost:5000 >/dev/null 2>&1 || true
fi

echo "Logs:"
echo "  Redis  -> logs/redis.log"
echo "  Celery -> logs/celery.log"
echo "  Flask  -> logs/flask.log"
echo "Utilise bash stop.sh pour arrêter les services."
tail -n 20 -f logs/redis.log logs/celery.log logs/flask.log
