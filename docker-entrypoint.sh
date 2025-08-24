#!/bin/bash

# Docker startup script with testing

echo "🐳 MCP Speech-to-Text Container Starting..."
echo "==========================================="

# Run functionality tests first
echo "🧪 Running functionality tests..."
python test_functionality.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests passed! Starting HTTP test server..."
    echo ""
    exec python http_server.py
else
    echo ""
    echo "❌ Tests failed! Check the logs above."
    echo "Container will exit in 30 seconds..."
    sleep 30
    exit 1
fi
