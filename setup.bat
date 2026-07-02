@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    where python >nul 2>nul && set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Python n'est pas installe.
    exit /b 1
)

if not exist requirements.txt (
    echo requirements.txt introuvable.
    exit /b 1
)

if not exist app.py (
    echo app.py introuvable.
    exit /b 1
)

call %PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

call %PYTHON_CMD% -c "from app import create_app; app = create_app(); print('Base SQLite prete: ' + app.config['SQLALCHEMY_DATABASE_URI'])"
if errorlevel 1 exit /b 1

echo Installation terminée!
