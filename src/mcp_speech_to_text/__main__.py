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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        "recommended_backend": None,
        "production_ready": False
    }
    
    logger.info(f"🔍 Detecting capabilities for {capabilities['platform']}")
    
    # Check Vosk availability (best for x86_64)
    try:
        import vosk
        capabilities["vosk_supported"] = True
        capabilities["offline_capable"] = True
        
        # Check if we can find or access a model
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        has_model = False
        if os.path.exists(models_dir):
            for item in os.listdir(models_dir):
                if item.startswith("vosk-model"):
                    has_model = True
                    break
        
        if has_model:
            logger.info("✅ Vosk available with model - full offline capabilities")
        else:
            logger.info("✅ Vosk available but no model found - will download automatically")
            
    except ImportError:
        logger.info("❌ Vosk not available")
    
    # Check SpeechRecognition availability
    try:
        import speech_recognition
        capabilities["speechrecognition_supported"] = True
        logger.info("✅ SpeechRecognition available")
    except ImportError:
        logger.info("❌ SpeechRecognition not available")
    
    # Determine best backend based on platform and availability
    if system == "linux" and machine == "x86_64" and capabilities["vosk_supported"]:
        capabilities["recommended_backend"] = "vosk"
        capabilities["production_ready"] = True
        logger.info("🎯 Using Vosk backend (optimal for x86_64 Linux production)")
    elif capabilities["vosk_supported"]:
        capabilities["recommended_backend"] = "vosk"
        capabilities["production_ready"] = True
        logger.info("🎯 Using Vosk backend (offline capable)")
    elif capabilities["speechrecognition_supported"]:
        capabilities["recommended_backend"] = "speechrecognition"
        capabilities["production_ready"] = system == "linux"
        logger.info("🎯 Using SpeechRecognition backend (requires internet)")
        if system == "darwin":
            logger.info("ℹ️  macOS detected - perfect for development and testing")
    else:
        logger.error("❌ No speech recognition backend available")
        capabilities["recommended_backend"] = None
    
    return capabilities

async def main():
    """Main entry point with automatic backend selection"""
    logger.info("🚀 Starting MCP Speech-to-Text Server...")
    
    # Detect capabilities
    caps = detect_platform_capabilities()
    logger.info(f"📊 Platform: {caps['platform']}")
    logger.info(f"📊 Offline capable: {caps['offline_capable']}")
    logger.info(f"📊 Production ready: {caps['production_ready']}")
    
    if not caps["recommended_backend"]:
        logger.error("❌ No speech recognition backend available. Please install:")
        logger.error("   🔹 For offline (x86_64): pip install vosk")
        logger.error("   🔹 For online/fallback: pip install SpeechRecognition")
        logger.error("   🔹 For audio processing: pip install pydub pyaudio")
        sys.exit(1)
    
    # Import and start the appropriate server
    try:
        if caps["recommended_backend"] == "vosk":
            from .server import OfflineSpeechToTextServer
            server = OfflineSpeechToTextServer()
            logger.info("✅ Vosk-based server initialized")
            
            # Check if model is available
            if server.vosk_model:
                logger.info("🎉 Ready for completely offline speech recognition!")
            else:
                logger.info("⚠️  No Vosk model loaded - use download_vosk_model tool to get started")
                
        else:  # speechrecognition
            from .server_sr import SpeechToTextServer
            server = SpeechToTextServer()
            logger.info("✅ SpeechRecognition-based server initialized")
            logger.info("🌐 Internet connection required for speech recognition")
        
        # Display startup summary
        logger.info("🎛️  Server Configuration:")
        logger.info(f"   • Backend: {caps['recommended_backend']}")
        logger.info(f"   • Offline: {caps['offline_capable']}")
        logger.info(f"   • Platform: {caps['platform']}")
        logger.info(f"   • Production: {caps['production_ready']}")
        
        # Run the server
        logger.info("🌟 MCP Speech-to-Text Server ready!")
        await server.run_server()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import server module: {e}")
        logger.error("💡 Make sure all dependencies are installed:")
        logger.error("   pip install -e .")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
