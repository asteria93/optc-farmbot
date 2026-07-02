@echo off
chcp 65001 >nul
echo ==============================
echo   OPTC Bot - Démarrage
echo ==============================
echo.

:: Démarrer Redis en arrière-plan (si disponible)
redis-server --daemonize yes >nul 2>&1
if not errorlevel 1 (
    echo [OK] Redis démarré
) else (
    echo [INFO] Redis non trouvé - utilisation du mode sans Redis
)
echo.

:: Démarrer Celery Worker dans une nouvelle fenêtre
echo Démarrage du worker Celery...
start "OPTC Celery Worker" cmd /c "celery -A celery_app worker --loglevel=info & pause"

:: Petite pause pour laisser Celery démarrer
timeout /t 2 /nobreak >nul

:: Démarrer Flask
echo Démarrage du serveur Flask...
echo.
echo ==============================
echo   Bot démarré!
echo   Ouvre: http://localhost:5000
echo ==============================
echo.

:: Ouvrir le navigateur automatiquement
start "" http://localhost:5000

:: Lancer Flask
python app.py
