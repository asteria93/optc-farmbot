@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"

for %%F in (flask celery redis) do (
    if exist ".run\%%F.pid" (
        set /p PID=<".run\%%F.pid"
        taskkill /PID !PID! /T /F >nul 2>nul
        del /f /q ".run\%%F.pid" >nul 2>nul
    )
)

taskkill /FI "WINDOWTITLE eq OPTC Flask" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq OPTC Celery" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq OPTC Redis" /T /F >nul 2>nul

echo Services arretes.
