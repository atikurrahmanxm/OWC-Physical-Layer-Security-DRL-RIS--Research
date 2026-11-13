@echo off
setlocal
cd /d "%~dp0"
echo ==============================================================================
echo       Optical RIS + Friendly Jamming Physical Layer Security Simulator
echo                     Supervisor Interactive Demonstration
echo ==============================================================================
echo.
echo Checking Python environment...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in PATH.
    echo Please install Python 3.10+ or run using an explicit Python executable.
    pause
    exit /b 1
)
echo Python found. Starting local simulation loopback server...
echo The browser will open http://127.0.0.1:[port]/demo automatically.
echo Press Ctrl+C in this terminal window to stop the demo server.
echo.
python launch_supervisor_demo.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTE] Demo server exited with code %ERRORLEVEL%.
    pause
)

