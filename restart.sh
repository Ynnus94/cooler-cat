#!/bin/bash
# Restart the CoolerCat server

echo "🔄 Restarting CoolerCat server..."

# Kill existing server process
pkill -f "python.*server.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Stopped existing server"
    sleep 1
else
    echo "ℹ No running server found"
fi

# Start the server
echo "🚀 Starting server..."
cd "$(dirname "$0")"
venv/bin/python scripts/server.py
