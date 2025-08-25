#!/bin/bash

# Simple Local Speech-to-Text Installation Script
# Works on macOS, Linux with uv or pip

set -e

echo "🎙️ Installing Local Speech-to-Text MCP Server..."
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install system dependencies on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 macOS detected - Installing portaudio..."
    if command -v brew >/dev/null 2>&1; then
        brew install portaudio
    else
        echo "⚠️  Please install Homebrew first: https://brew.sh"
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing dependencies..."

if command -v uv >/dev/null 2>&1; then
    echo "Using uv (recommended)..."
    uv sync
    uv pip install vosk
else
    echo "Using pip..."
    pip install -e ".[offline]"
fi

# Download English model
echo "🌐 Downloading English speech model..."
mkdir -p src/mcp_speech_to_text/models
cd src/mcp_speech_to_text/models

if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    if command -v wget >/dev/null 2>&1; then
        wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    else
        curl -s -o vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    fi
    
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    echo "✅ Model downloaded"
else
    echo "✅ Model already exists"
fi

cd ../../..

# Test installation
echo "🧪 Testing installation..."
if command -v uv >/dev/null 2>&1; then
    uv run python -c "
from mcp_speech_to_text.server import OfflineSpeechToTextServer
server = OfflineSpeechToTextServer()
print('✅ Installation successful!')
"
else
    python -c "
from mcp_speech_to_text.server import OfflineSpeechToTextServer
server = OfflineSpeechToTextServer()
print('✅ Installation successful!')
"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 To run the server:"
if command -v uv >/dev/null 2>&1; then
    echo "   uv run mcp-speech-to-text"
else
    echo "   python -m mcp_speech_to_text.server"
fi
echo ""
echo "✨ Features:"
echo "   • Completely offline - no internet needed"
echo "   • Works in Hong Kong and any region"
echo "   • No API costs"
echo "   • Privacy-first - audio stays local"
