@echo off
REM OPTC Farming Bot - Windows setup script

echo ======================================
echo   OPTC Farming Bot - Setup
echo ======================================
echo.

REM --- Python check ---
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found
for /f "tokens=2" %%V in ('python --version 2^>^&1') do echo     Version: %%V

REM --- Virtual environment ---
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM --- Activate ---
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM --- Dependencies ---
echo.
echo Installing Python dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] Dependencies installed

REM --- Environment file ---
if not exist ".env" (
    copy .env.example .env >nul
    echo.
    echo [OK] .env file created from .env.example
    echo.
    echo   *** ACTION REQUIRED ***
    echo   Edit .env and set a secure SECRET_KEY before running in production.
) else (
    echo [OK] .env already exists (not overwritten)
)

REM --- Logs directory ---
if not exist "logs\" mkdir logs
echo [OK] logs\ directory ready

REM --- Database ---
echo.
echo Initializing database...
python scripts\init_db.py
echo [OK] Database initialized

REM --- Redis reminder ---
echo.
echo NOTE: Redis must be running before you start the bot.
echo   Download: https://github.com/microsoftarchive/redis/releases
echo   Or use Docker: docker run -d -p 6379:6379 redis:alpine

echo.
echo ======================================
echo   Setup complete!
echo ======================================
echo.
echo Next steps:
echo   1. Edit .env with your settings (especially SECRET_KEY)
echo   2. Start Redis (redis-server.exe or Docker)
echo   3. Run: start.bat
echo.
pause
