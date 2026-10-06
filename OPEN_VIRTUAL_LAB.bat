@echo off
title Opening OWC Virtual Security Lab
cd /d "%~dp0"
echo ========================================================
echo  Launching Interactive OWC 3D Virtual Security Lab
echo ========================================================
echo.
echo Opening virtual_lab.html in your default web browser...
start "" "virtual_lab.html"
echo.
echo Lab is running in your browser!
echo You can drag Bob and Eve with your mouse to test live secrecy metrics.
timeout /t 3
