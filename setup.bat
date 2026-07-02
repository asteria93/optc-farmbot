@echo off
chcp 65001 >nul
echo ==============================
echo   OPTC Bot - Setup Windows
echo ==============================
echo.

:: Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe!
    echo Telecharge Python sur: https://www.python.org/downloads/
    echo Coche "Add Python to PATH" pendant l'installation.
    pause
    exit /b 1
)

echo [OK] Python trouve
echo.

:: Installer les dépendances
echo Installation des dépendances...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Échec de l'installation des dépendances.
    pause
    exit /b 1
)
echo [OK] Dépendances installées
echo.

:: Copier .env si nécessaire
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [OK] Fichier .env créé
    )
)

:: Initialiser la base de données
echo Initialisation de la base de données...
python scripts/init_db.py
echo [OK] Base de données initialisée
echo.

echo ==============================
echo   Setup terminé avec succès!
echo   Lance maintenant: start.bat
echo ==============================
pause
