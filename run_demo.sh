#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🎪 Feria de Sevilla - AI Agent Demo Launcher 🎪"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "Checking/Installing dependencies..."
pip install -r requirements.txt

# Copy assets to frontend
echo "Copying assets to frontend..."
cp data/cartel_feria_2025.jpeg src/frontend/

# Function to kill background tasks on exit
cleanup() {
    echo -e "\n🛑 Stopping servers..."
    kill $(jobs -p)
    exit
}
trap cleanup EXIT

# Start backend
echo "🚀 Starting Backend (Port 8000)..."
python3 src/backend/agent.py &

# Start frontend
echo "🌐 Starting Frontend (Port 3000)..."
cd src/frontend
python3 -m http.server 3000 &

# Wait for background processes
echo "✨ Demo is running! Press Ctrl+C to stop both servers."
wait
