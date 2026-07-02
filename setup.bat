@echo off
echo Installation du bot OPTC...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe!
    echo Telecharge Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python est installe.
echo.

echo Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo Erreur lors de l'installation des dependances!
    pause
    exit /b 1
)
echo.

echo Creation de la base de donnees...
python -c "from app import create_app; from models import db; app = create_app(); print('Base de donnees creee!')"
if errorlevel 1 (
    echo Erreur lors de la creation de la base de donnees!
    pause
    exit /b 1
)
echo.

if not exist .env (
    copy .env.example .env
    echo Fichier .env cree depuis .env.example
    echo Modifie .env si necessaire.
    echo.
)

echo ================================
echo Installation terminee!
echo.
echo Pour demarrer le bot, double-clic sur start.bat
echo ================================
pause
