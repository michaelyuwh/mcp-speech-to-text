#!/bin/bash
# n8n MCP Server Startup Script

echo "🚀 Starting MCP Speech-to-Text Server for n8n..."
echo "Using stdio interface (MCP protocol)"

# Set environment variables
export PYTHONPATH=/app/src
export WHISPER_MODEL_SIZE=base
export DEFAULT_LANGUAGE=auto

# Run the MCP server using stdio interface
cd /app
exec python -m mcp_speech_to_text.server
