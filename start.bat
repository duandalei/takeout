@echo off
title Takeout System

echo ============================
echo   Takeout System - Starting
echo ============================
echo.

cd /d "%~dp0"

echo Starting Flask app...
start "" http://127.0.0.1:5000

conda run -n takeout python run.py

echo.
echo App exited.
pause
