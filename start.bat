@echo off
echo ==============================
echo   OPTC Bot - Demarrage
echo ==============================
echo.

:: Demarrer Redis en arriere-plan (si disponible)
redis-server --daemonize yes >nul 2>&1
if not errorlevel 1 (
    echo [OK] Redis demarre
) else (
    echo [INFO] Redis non trouve - utilisation du mode sans Redis
)
echo.

:: Demarrer Celery Worker dans une nouvelle fenetre
echo Demarrage du worker Celery...
start "OPTC Celery Worker" cmd /c "celery -A celery_app worker --loglevel=info & pause"

:: Petite pause pour laisser Celery demarrer
timeout /t 2 /nobreak >nul

:: Demarrer Flask
echo Demarrage du serveur Flask...
echo.
echo ==============================
echo   Bot demarre!
echo   Ouvre: http://localhost:5000
echo ==============================
echo.

:: Ouvrir le navigateur automatiquement
start "" http://localhost:5000

:: Lancer Flask
python app.py
