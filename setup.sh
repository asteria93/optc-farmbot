#!/bin/bash
echo "Installation du bot OPTC..."
echo ""

python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Python3 n'est pas installe!"
    echo "Installe Python3 avec: sudo apt install python3 python3-pip (Linux)"
    echo "ou depuis: https://www.python.org/downloads/ (Mac)"
    exit 1
fi

echo "Python3 est installe."
echo ""

echo "Installation des dependances..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erreur lors de l'installation des dependances!"
    exit 1
fi
echo ""

echo "Creation de la base de donnees..."
python3 -c "from app import create_app; from models import db; app = create_app(); print('Base de donnees creee!')"
if [ $? -ne 0 ]; then
    echo "Erreur lors de la creation de la base de donnees!"
    exit 1
fi
echo ""

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env cree depuis .env.example"
    echo "Modifie .env si necessaire."
    echo ""
fi

echo "================================"
echo "Installation terminee!"
echo ""
echo "Pour demarrer le bot: bash start.sh"
echo "================================"
