#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python est requis mais introuvable."
  exit 1
fi

cd "$REPO_ROOT"

echo "Installation des dépendances..."
"$PYTHON_CMD" -m pip install -r requirements.txt

echo "Initialisation de la base de données..."
"$PYTHON_CMD" scripts/init_db.py

echo "Tout est prêt!"
