@echo off
echo Demarrage du bot OPTC...
echo.

echo Demarrage de Redis...
where redis-server >nul 2>&1
if not errorlevel 1 (
    start "" /B redis-server
    timeout /t 2 /nobreak >nul
    echo Redis demarre.
) else (
    echo Redis non trouve - le bot fonctionnera sans file de taches.
    echo Telecharge Redis depuis: https://github.com/microsoftarchive/redis/releases
)
echo.

echo Demarrage de Celery Worker...
start "Celery Worker" cmd /k "celery -A celery_app worker --loglevel=info && pause"
timeout /t 3 /nobreak >nul
echo.

echo Demarrage de Flask...
echo Dashboard disponible sur: http://localhost:5000
echo.
python app.py
