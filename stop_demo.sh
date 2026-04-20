#!/bin/bash

echo "🛑 Stopping Feria de Sevilla Demo..."

# Function to stop process on a port
stop_port() {
    local port=$1
    local pid=$(lsof -t -i :$port)
    if [ -z "$pid" ]; then
        echo "No process found on port $port"
    else
        echo "Stopping process $pid on port $port..."
        kill $pid
        # Wait a bit for it to stop
        sleep 1
        # Check if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Process $pid did not stop, forcing..."
            kill -9 $pid
        fi
    fi
}

# Stop frontend (Port 3000)
stop_port 3000

# Stop backend (Port 8000)
stop_port 8000

echo "✨ Done!"
