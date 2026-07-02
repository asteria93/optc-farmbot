#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

stop_pid_file() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill "$pid" >/dev/null 2>&1; then
      wait "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
}

stop_pid_file .run/flask.pid
stop_pid_file .run/celery.pid
stop_pid_file .run/redis.pid

pkill -f "celery -A celery_app worker --loglevel=info" >/dev/null 2>&1 || true
pkill -f "python app.py" >/dev/null 2>&1 || true
pkill -f "python3 app.py" >/dev/null 2>&1 || true
pkill -f "redis-server" >/dev/null 2>&1 || true

echo "Services arrêtés."
