#!/bin/bash
# Uptime Control Plane Launcher for macOS/Linux

echo ""
echo "==============================================="
echo "  Uptime Control Plane Launcher"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "[ERROR] main.py not found. Are you in the control_plane directory?"
    exit 1
fi

# Install requirements
echo "[*] Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

# Run the server
echo "[*] Starting Control Plane on http://localhost:8000"
echo "[*] Press Ctrl+C to stop"
echo ""
python3 main.py