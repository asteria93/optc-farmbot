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

where redis-server >nul 2>nul
if errorlevel 1 (
    echo redis-server est introuvable.
    exit /b 1
)

where celery >nul 2>nul
if errorlevel 1 (
    echo celery est introuvable.
    exit /b 1
)

if not exist logs mkdir logs
if not exist .run mkdir .run

powershell -NoProfile -Command "$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/k','title OPTC Redis && cd /d ""%CD%"" && redis-server' -PassThru; Set-Content '.run\redis.pid' $p.Id"
powershell -NoProfile -Command "$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/k','title OPTC Celery && cd /d ""%CD%"" && celery -A celery_app worker --loglevel=info' -PassThru; Set-Content '.run\celery.pid' $p.Id"
powershell -NoProfile -Command "$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/k','title OPTC Flask && cd /d ""%CD%"" && %PYTHON_CMD% app.py' -PassThru; Set-Content '.run\flask.pid' $p.Id"

start "" http://localhost:5000
echo Services lances. Les logs sont affiches dans les nouvelles fenetres.
