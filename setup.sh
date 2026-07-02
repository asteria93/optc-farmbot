#!/bin/bash
echo "Installation du bot OPTC..."
echo ""

python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Python3 n'est pas installé!"
    echo "Installe Python3 avec: sudo apt install python3 python3-pip (Linux)"
    echo "ou depuis: https://www.python.org/downloads/ (Mac)"
    exit 1
fi

echo "Python3 est installé."
echo ""

echo "Installation des dépendances..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erreur lors de l'installation des dépendances!"
    exit 1
fi
echo ""

echo "Création de la base de données..."
python3 -c "from app import create_app; from models import db; app = create_app(); print('Base de données créée!')"
if [ $? -ne 0 ]; then
    echo "Erreur lors de la création de la base de données!"
    exit 1
fi
echo ""

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé depuis .env.example"
    echo "Modifie .env si nécessaire."
    echo ""
fi

echo "================================"
echo "Installation terminée!"
echo ""
echo "Pour démarrer le bot: bash start.sh"
echo "================================"
