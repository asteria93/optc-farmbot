#!/bin/bash
echo "=============================="
echo "  OPTC Bot - Setup Mac/Linux"
echo "=============================="
echo ""

# Verifier Python
if ! command -v python3 &>/dev/null; then
    echo "[ERREUR] Python3 n'est pas installe!"
    echo "Sur Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "Sur Mac: brew install python3"
    exit 1
fi

echo "[OK] Python trouve: $(python3 --version)"
echo ""

# Installer les dependances
echo "Installation des dependances..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERREUR] Echec de l'installation des dependances."
    exit 1
fi
echo "[OK] Dependances installees"
echo ""

# Copier .env si necessaire
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "[OK] Fichier .env cree"
fi

# Initialiser la base de donnees
echo "Initialisation de la base de donnees..."
python3 scripts/init_db.py
echo "[OK] Base de donnees initialisee"
echo ""

echo "=============================="
echo "  Setup termine avec succes!"
echo "  Lance maintenant: bash start.sh"
echo "=============================="
