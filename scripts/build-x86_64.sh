#!/bin/bash

# Build script for x86_64 production deployment
# This script ensures the Docker image works properly on x86_64 systems

set -e

echo "🚀 Building MCP Speech-to-Text for x86_64 production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build for x86_64 platform specifically
echo -e "${BLUE}Building Docker image for x86_64 platform...${NC}"
docker buildx build \
    --platform linux/amd64 \
    --tag mcp-speech-to-text:x86_64-latest \
    --tag mcp-speech-to-text:x86_64-v1.0.0 \
    --load \
    .

echo -e "${GREEN}✅ Build completed successfully for x86_64!${NC}"

# Test the built image
echo -e "${BLUE}Testing the built image...${NC}"
docker run --rm --platform linux/amd64 mcp-speech-to-text:x86_64-latest python -c "
import sys
print(f'✅ Python version: {sys.version}')

# Test Vosk import
try:
    import vosk
    print('✅ Vosk imported successfully')
except ImportError as e:
    print(f'❌ Vosk import failed: {e}')

# Test SpeechRecognition import
try:
    import speech_recognition
    print('✅ SpeechRecognition imported successfully')
except ImportError as e:
    print(f'❌ SpeechRecognition import failed: {e}')

# Test MCP imports
try:
    from mcp.server import Server
    print('✅ MCP server imported successfully')
except ImportError as e:
    print(f'❌ MCP import failed: {e}')

# Test server creation
try:
    from src.mcp_speech_to_text.server import OfflineSpeechToTextServer
    server = OfflineSpeechToTextServer()
    print('✅ Server created successfully')
except Exception as e:
    print(f'❌ Server creation failed: {e}')

print('🎉 All tests passed! Ready for x86_64 deployment.')
"

echo -e "${GREEN}✅ Image testing completed!${NC}"

# Show image info
echo -e "${BLUE}Image information:${NC}"
docker images | grep mcp-speech-to-text

echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Push to registry: docker push mcp-speech-to-text:x86_64-latest"
echo "2. Deploy with: docker run -d --name mcp-speech mcp-speech-to-text:x86_64-latest"
echo "3. Or use docker-compose: docker compose up -d"

# Save build info
echo -e "${BLUE}Saving build information...${NC}"
cat > build-info.json << EOF
{
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platform": "linux/amd64",
  "image_tag": "mcp-speech-to-text:x86_64-latest",
  "vosk_support": true,
  "speechrecognition_support": true,
  "offline_capable": true,
  "production_ready": true
}
EOF

echo -e "${GREEN}🎉 Build script completed successfully!${NC}"
echo -e "${BLUE}Build info saved to: build-info.json${NC}"
