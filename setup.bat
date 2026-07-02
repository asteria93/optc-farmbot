@echo off
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

:: Installer les dependances
echo Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo [OK] Dependances installees
echo.

:: Copier .env si necessaire
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [OK] Fichier .env cree
    )
)

:: Initialiser la base de donnees
echo Initialisation de la base de donnees...
python scripts/init_db.py
echo [OK] Base de donnees initialisee
echo.

echo ==============================
echo   Setup termine avec succes!
echo   Lance maintenant: start.bat
echo ==============================
pause
