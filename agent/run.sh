#!/bin/bash
REM Uptime Agent Launcher for macOS/Linux

echo ""
echo "==============================================="
echo "  Uptime Agent Launcher"
echo "==============================================="
echo ""

REM Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

REM Check if we're in the right directory
if [ ! -f "agent.py" ]; then
    echo "[ERROR] agent.py not found. Are you in the agent directory?"
    exit 1
fi

REM Install requirements
echo "[*] Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

REM Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[WARNING] Docker is not installed or not in PATH"
    echo "Docker is required to run jobs. Please install it from https://www.docker.com/"
    echo ""
fi

REM Run the agent
echo "[*] Starting Agent..."
echo "[*] Press Ctrl+C to stop"
echo ""
python3 agent.py --price 0.10 --name "device-1" --url http://localhost:8000