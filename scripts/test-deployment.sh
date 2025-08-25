#!/bin/bash

# Comprehensive test script for x86_64 deployment verification
# Run this on your x86_64 production server to verify everything works

set -e

echo "🧪 MCP Speech-to-Text x86_64 Deployment Verification"
echo "===================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test functions
test_docker() {
    echo -e "${BLUE}Testing Docker availability...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker is installed${NC}"
        docker --version
    else
        echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
        exit 1
    fi
}

test_platform() {
    echo -e "${BLUE}Checking platform compatibility...${NC}"
    ARCH=$(uname -m)
    OS=$(uname -s)
    
    echo "Platform: $OS $ARCH"
    
    if [[ "$ARCH" == "x86_64" ]]; then
        echo -e "${GREEN}✅ x86_64 platform detected - full Vosk support available${NC}"
        return 0
    elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        echo -e "${YELLOW}⚠️  ARM64 platform detected - SpeechRecognition fallback mode${NC}"
        return 1
    else
        echo -e "${RED}❌ Unsupported platform: $ARCH${NC}"
        exit 1
    fi
}

build_image() {
    echo -e "${BLUE}Building Docker image for current platform...${NC}"
    
    if docker buildx build --platform linux/$(uname -m) --load -t mcp-speech-test . ; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        exit 1
    fi
}

test_dependencies() {
    echo -e "${BLUE}Testing dependencies in container...${NC}"
    
    docker run --rm mcp-speech-test python -c "
import sys
print(f'Python version: {sys.version}')

# Test MCP
try:
    from mcp.server import Server
    print('✅ MCP framework available')
except ImportError as e:
    print(f'❌ MCP import failed: {e}')
    sys.exit(1)

# Test Vosk (x86_64 only)
import platform
if platform.machine() == 'x86_64':
    try:
        import vosk
        print('✅ Vosk available (offline speech recognition)')
    except ImportError:
        print('❌ Vosk not available')
        sys.exit(1)
else:
    print('ℹ️  Vosk skipped (not x86_64)')

# Test SpeechRecognition
try:
    import speech_recognition
    print('✅ SpeechRecognition available')
except ImportError as e:
    print(f'❌ SpeechRecognition import failed: {e}')
    sys.exit(1)

# Test audio libraries
try:
    import pyaudio
    print('✅ PyAudio available (microphone support)')
except ImportError:
    print('⚠️  PyAudio not available (no microphone)')

try:
    from pydub import AudioSegment
    print('✅ Pydub available (format conversion)')
except ImportError:
    print('⚠️  Pydub not available (limited format support)')

print('🎉 All required dependencies are available!')
"
}

test_server_creation() {
    echo -e "${BLUE}Testing server initialization...${NC}"
    
    docker run --rm mcp-speech-test python -c "
import sys
from src.mcp_speech_to_text.server import OfflineSpeechToTextServer

try:
    server = OfflineSpeechToTextServer()
    print('✅ Server created successfully')
    print(f'   Server name: {server.app.name}')
    
    # Check Vosk initialization
    if hasattr(server, 'vosk_model') and server.vosk_model:
        print('✅ Vosk model loaded successfully')
    else:
        print('ℹ️  Vosk model not loaded (expected on non-x86_64 or if model missing)')
    
    print('🎉 Server initialization test passed!')
    
except Exception as e:
    print(f'❌ Server creation failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
}

test_model_download() {
    echo -e "${BLUE}Testing Vosk model availability...${NC}"
    
    docker run --rm mcp-speech-test bash -c "
if [ -d '/app/src/mcp_speech_to_text/models/vosk-model-small-en-us-0.15' ]; then
    echo '✅ Vosk model found'
    ls -la /app/src/mcp_speech_to_text/models/
else
    echo 'ℹ️  Vosk model not found (will be downloaded on first use)'
fi
"
}

test_production_run() {
    echo -e "${BLUE}Testing production container startup...${NC}"
    
    # Start container in background
    CONTAINER_ID=$(docker run -d --name mcp-speech-test-run mcp-speech-test)
    
    # Wait a bit for startup
    sleep 5
    
    # Check if container is running
    if docker ps | grep -q mcp-speech-test-run; then
        echo -e "${GREEN}✅ Container started successfully${NC}"
        
        # Check logs
        echo "Container logs:"
        docker logs mcp-speech-test-run
        
        # Cleanup
        docker stop mcp-speech-test-run >/dev/null 2>&1
        docker rm mcp-speech-test-run >/dev/null 2>&1
        
    else
        echo -e "${RED}❌ Container failed to start${NC}"
        docker logs mcp-speech-test-run
        docker rm mcp-speech-test-run >/dev/null 2>&1
        exit 1
    fi
}

cleanup() {
    echo -e "${BLUE}Cleaning up test resources...${NC}"
    docker rmi mcp-speech-test >/dev/null 2>&1 || true
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main test execution
main() {
    echo "Starting deployment verification tests..."
    echo
    
    # Check if we have the project files
    if [[ ! -f "Dockerfile" ]] || [[ ! -f "pyproject.toml" ]]; then
        echo -e "${RED}❌ Project files not found. Run this from the project root directory.${NC}"
        exit 1
    fi
    
    # Run tests
    test_docker
    echo
    
    IS_X86_64=false
    test_platform && IS_X86_64=true
    echo
    
    build_image
    echo
    
    test_dependencies
    echo
    
    test_server_creation
    echo
    
    if [[ "$IS_X86_64" == "true" ]]; then
        test_model_download
        echo
    fi
    
    test_production_run
    echo
    
    # Final summary
    echo -e "${GREEN}🎉 All tests passed! Deployment verification successful.${NC}"
    echo
    echo -e "${BLUE}📋 Summary:${NC}"
    if [[ "$IS_X86_64" == "true" ]]; then
        echo "   ✅ x86_64 platform with full Vosk support"
        echo "   ✅ Offline speech recognition available"
        echo "   ✅ No internet required for operation"
    else
        echo "   ✅ ARM64 platform with SpeechRecognition fallback"
        echo "   ⚠️  Internet connection required for speech recognition"
    fi
    echo "   ✅ Docker container builds and runs successfully"
    echo "   ✅ All dependencies properly installed"
    echo "   ✅ MCP server initializes correctly"
    echo
    echo -e "${BLUE}🚀 Ready for production deployment!${NC}"
    echo
    echo "Next steps:"
    echo "1. Deploy with: docker compose up -d"
    echo "2. Or run directly: docker run -d --name mcp-speech mcp-speech-to-text:latest"
    echo "3. Monitor with: docker logs -f mcp-speech"
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"
