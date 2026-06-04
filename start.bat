@echo off
title Takeout System

echo ============================
echo   Takeout System - Starting
echo ============================
echo.

cd /d "C:\Users\段大磊\Desktop\takeout"

echo Starting Flask app...
start "" http://127.0.0.1:5000

D:\develop\Anaconda\envs\takeout\python.exe run.py

echo.
echo App exited.
pause
