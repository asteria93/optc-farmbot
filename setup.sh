#!/bin/bash
echo "=============================="
echo "  OPTC Bot - Setup Mac/Linux"
echo "=============================="
echo ""

# Vérifier Python
if ! command -v python3 &>/dev/null; then
    echo "[ERREUR] Python3 n'est pas installé!"
    echo "Sur Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "Sur Mac: brew install python3"
    exit 1
fi

echo "[OK] Python trouvé: $(python3 --version)"
echo ""

# Installer les dépendances
echo "Installation des dépendances..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de l'installation des dépendances."
    exit 1
fi
echo "[OK] Dépendances installées"
echo ""

# Copier .env si nécessaire
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "[OK] Fichier .env créé"
fi

# Initialiser la base de données
echo "Initialisation de la base de données..."
python3 scripts/init_db.py
echo "[OK] Base de données initialisée"
echo ""

echo "=============================="
echo "  Setup terminé avec succès!"
echo "  Lance maintenant: bash start.sh"
echo "=============================="
