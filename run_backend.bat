@echo off
title StegoGuard - FastAPI Backend Server
echo ========================================================
echo        Starting StegoGuard Backend & Web UI
echo ========================================================
echo.
echo Checking Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo.
echo Starting FastAPI Server on http://127.0.0.1:8000 ...
echo The web app will be available at: http://127.0.0.1:8000
echo API Docs will be available at:    http://127.0.0.1:8000/docs
echo.
python server.py
pause
