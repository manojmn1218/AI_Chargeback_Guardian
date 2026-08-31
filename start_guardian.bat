@echo off
title AI Chargeback Guardian - Supervisor
cd /d "%~dp0"
echo ================================================================
echo           AI CHARGEBACK GUARDIAN - SERVER SUPERVISOR
echo ================================================================
echo Starting backend and unified frontend application on http://localhost:8000
echo.
backend\venv\Scripts\python.exe run_guardian.py %*
pause
