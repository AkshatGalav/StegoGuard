@echo off
title StegoGuard - React Frontend (Dev Server)
echo ========================================================
echo        Starting StegoGuard React Frontend Dev Server
echo ========================================================
echo.
cd frontend
if not exist node_modules (
    echo node_modules not found. Running npm install...
    call npm install
)
echo.
echo Starting Vite Dev Server...
call npm run dev
pause
