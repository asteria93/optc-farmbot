@echo off
REM OPTC Farming Bot - Windows start script
REM Opens Celery worker and Flask server in separate windows.

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo ======================================
echo   OPTC Farming Bot - Starting
echo ======================================
echo.

REM --- Virtual environment check ---
if not exist "venv\" (
    echo ERROR: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM --- .env check ---
if not exist ".env" (
    echo ERROR: .env not found. Run setup.bat first.
    pause
    exit /b 1
)

if not exist "logs\" mkdir logs

REM --- Celery worker (new window) ---
echo Starting Celery worker in a new window...
start "OPTC Celery Worker" cmd /k "call venv\Scripts\activate.bat && celery -A app.celery worker --loglevel=info --pool=solo"
echo [OK] Celery window opened

REM Give Celery time to connect
timeout /t 3 /nobreak >nul

REM --- Flask web server ---
echo Starting Flask web server...
echo.
echo ======================================
echo   Dashboard: http://localhost:5000
echo   Press Ctrl+C to stop
echo ======================================
echo.
call venv\Scripts\activate.bat
python app.py
