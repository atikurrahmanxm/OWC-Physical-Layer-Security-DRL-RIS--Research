@echo off
title OWC Physical Layer Security - Simulation Dashboard
cd /d "%~dp0"
echo ========================================================
echo  Launching Optical Wireless Communication GUI Dashboard
echo ========================================================
python gui_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Could not start GUI dashboard.
    echo Make sure Python and required libraries are installed.
    pause
)
