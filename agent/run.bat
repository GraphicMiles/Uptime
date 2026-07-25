@echo off
REM Uptime Agent Launcher for Windows

echo.
echo ===============================================
echo  Uptime Agent Launcher
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
if not exist "agent.py" (
    echo [ERROR] agent.py not found. Are you in the agent directory?
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

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not installed or not in PATH
    echo Docker is required to run jobs. Please install it from https://www.docker.com/
    echo.
)

REM Run the agent
echo [*] Starting Agent...
echo [*] Press Ctrl+C to stop
echo.
python agent.py --price 0.10 --name "device-1" --url http://localhost:8000
pause