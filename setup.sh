#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python n'est pas installé."
  exit 1
fi

if [[ ! -f requirements.txt ]]; then
  echo "requirements.txt introuvable."
  exit 1
fi

if [[ ! -f app.py ]]; then
  echo "app.py introuvable."
  exit 1
fi

"$PYTHON_CMD" -m pip install -r requirements.txt
"$PYTHON_CMD" -c "from app import create_app; app = create_app(); print(f\"Base SQLite prête: {app.config['SQLALCHEMY_DATABASE_URI']}\")"

echo "Installation terminée!"
