@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"

call :find_python
if not defined PYTHON_CMD exit /b 1

%PYTHON_CMD% -c "import flask, celery, redis" >nul 2>&1
if errorlevel 1 (
  echo Installation des dependances...
  %PYTHON_CMD% -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)

call :start_redis
if errorlevel 1 exit /b 1

echo Demarrage du worker Celery...
start "Celery Worker" /D "%REPO_ROOT%" cmd /c "%PYTHON_CMD% -m celery -A celery_app:celery_app worker --loglevel=info"

start "" http://localhost:5000

echo Demarrage de Flask sur http://localhost:5000 ...
%PYTHON_CMD% app.py
exit /b %errorlevel%

:start_redis
where redis-cli >nul 2>&1
if not errorlevel 1 (
  redis-cli ping >nul 2>&1
  if not errorlevel 1 (
    echo Redis est deja lance.
    exit /b 0
  )
)

where redis-server >nul 2>&1
if errorlevel 1 (
  echo redis-server est introuvable. Installe Redis puis relance le script.
  exit /b 1
)

echo Demarrage de Redis...
start "Redis" /D "%REPO_ROOT%" cmd /c "redis-server"
timeout /t 3 >nul
exit /b 0

:find_python
py -3 --version >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  goto :eof
)

python --version >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  goto :eof
)

echo Python est requis mais introuvable.
exit /b 1
