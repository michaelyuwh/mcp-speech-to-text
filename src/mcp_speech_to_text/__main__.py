#!/usr/bin/env python3
"""
MCP Speech-to-Text Server Entry Point
Automatically detects platform and uses the best available backend
"""

import asyncio
import platform
import sys
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_platform_capabilities():
    """Detect platform and available speech recognition capabilities"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    capabilities = {
        "platform": f"{system}-{machine}",
        "vosk_supported": False,
        "speechrecognition_supported": False,
        "offline_capable": False,
        "recommended_backend": None
    }
    
    # Check Vosk availability
    try:
        import vosk
        capabilities["vosk_supported"] = True
        capabilities["offline_capable"] = True
        logger.info("✅ Vosk available - offline speech recognition enabled")
    except ImportError:
        logger.info("❌ Vosk not available")
    
    # Check SpeechRecognition availability
    try:
        import speech_recognition
        capabilities["speechrecognition_supported"] = True
        logger.info("✅ SpeechRecognition available")
    except ImportError:
        logger.info("❌ SpeechRecognition not available")
    
    # Determine best backend
    if capabilities["vosk_supported"]:
        capabilities["recommended_backend"] = "vosk"
        logger.info("🎯 Using Vosk backend (best for offline)")
    elif capabilities["speechrecognition_supported"]:
        capabilities["recommended_backend"] = "speechrecognition"
        logger.info("🎯 Using SpeechRecognition backend (requires internet)")
    else:
        logger.error("❌ No speech recognition backend available")
        capabilities["recommended_backend"] = None
    
    return capabilities

async def main():
    """Main entry point with automatic backend selection"""
    logger.info("🚀 Starting MCP Speech-to-Text Server...")
    
    # Detect capabilities
    caps = detect_platform_capabilities()
    logger.info(f"Platform: {caps['platform']}")
    logger.info(f"Offline capable: {caps['offline_capable']}")
    
    if not caps["recommended_backend"]:
        logger.error("❌ No speech recognition backend available. Please install:")
        logger.error("   - For offline: pip install vosk")
        logger.error("   - For online: pip install SpeechRecognition")
        sys.exit(1)
    
    # Import and start the appropriate server
    try:
        if caps["recommended_backend"] == "vosk":
            from .server import OfflineSpeechToTextServer
            server = OfflineSpeechToTextServer()
            logger.info("✅ Vosk-based server initialized")
        else:
            from .server_sr import SpeechToTextServer
            server = SpeechToTextServer()
            logger.info("✅ SpeechRecognition-based server initialized")
        
        # Run the server
        await server.run_server()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import server module: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
