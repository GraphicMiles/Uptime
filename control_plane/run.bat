@echo off
REM Uptime Control Plane Launcher for Windows

echo.
echo ===============================================
echo  Uptime Control Plane Launcher
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo [ERROR] main.py not found. Are you in the control_plane directory?
    pause
    exit /b 1
)

REM Install requirements
echo [*] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Run the server
echo [*] Starting Control Plane on http://localhost:8000
echo [*] Press Ctrl+C to stop
echo.
python main.py
pause