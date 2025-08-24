#!/bin/bash

# MCP Speech-to-Text Server Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎤 MCP Speech-to-Text Server v1.0.0${NC}"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed. Please install it first:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Set default environment variables
export WHISPER_MODEL_SIZE=${WHISPER_MODEL_SIZE:-"base"}
export DEFAULT_LANGUAGE=${DEFAULT_LANGUAGE:-"auto"}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Whisper Model: $WHISPER_MODEL_SIZE"
echo "  Default Language: $DEFAULT_LANGUAGE"
echo "  Log Level: $LOG_LEVEL"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo -e "${GREEN}🐳 Running in Docker container${NC}"
    export PYTHONPATH=/app/src
    cd /app
else
    echo -e "${GREEN}💻 Running locally${NC}"
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        uv venv
    fi
    
    # Activate virtual environment and install dependencies
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    uv pip install -e .
    
    # Set PYTHONPATH
    export PYTHONPATH=$(pwd)/src
fi

# Download Whisper model if needed
echo -e "${YELLOW}🤖 Checking Whisper model...${NC}"
python -c "import whisper; whisper.load_model('$WHISPER_MODEL_SIZE')" 2>/dev/null || {
    echo -e "${YELLOW}📥 Downloading Whisper model ($WHISPER_MODEL_SIZE)...${NC}"
    python -c "import whisper; whisper.load_model('$WHISPER_MODEL_SIZE')"
}

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}🚀 Starting MCP Speech-to-Text server...${NC}"
echo ""

# Start the server
exec python -m mcp_speech_to_text.server
