@echo off
setlocal

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

call :find_python
if not defined PYTHON_CMD exit /b 1

echo Installation des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Initialisation de la base de donnees...
%PYTHON_CMD% scripts\init_db.py
if errorlevel 1 exit /b 1

echo Tout est pret!
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
