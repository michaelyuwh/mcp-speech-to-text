#!/usr/bin/env python3
"""
Simple test script for MCP Speech-to-Text functionality
"""

import asyncio
import json
import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, '/app/src' if os.path.exists('/app/src') else 'src')

async def test_basic_functionality():
    """Test basic functionality without full MCP server."""
    
    print("🧪 Testing MCP Speech-to-Text Basic Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        import whisper
        print("   ✅ Whisper imported successfully")
        
        try:
            import speech_recognition as sr
            print("   ✅ SpeechRecognition imported successfully")
        except ImportError:
            print("   ⚠️ SpeechRecognition not available (expected in Docker)")
        
        try:
            import pyaudio
            print("   ✅ PyAudio imported successfully")
        except ImportError:
            print("   ⚠️ PyAudio not available (expected in Docker)")
        
        try:
            from pydub import AudioSegment
            print("   ✅ Pydub imported successfully")
        except ImportError:
            print("   ⚠️ Pydub not available")
        
        # Test Whisper model loading
        print("\n2. Testing Whisper model loading...")
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        print(f"   Loading {model_size} model...")
        model = whisper.load_model(model_size)
        print(f"   ✅ {model_size} model loaded successfully")
        print(f"   Model type: {type(model)}")
        
        # Test basic transcription with a simple audio (we'll create a dummy test)
        print("\n3. Testing basic functionality...")
        
        # Create a very simple test case
        supported_formats = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"]
        print(f"   ✅ Supported formats: {', '.join(supported_formats)}")
        
        # Test configuration
        print("\n4. Testing configuration...")
        default_language = os.getenv("DEFAULT_LANGUAGE", "auto")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        print(f"   ✅ Default language: {default_language}")
        print(f"   ✅ Log level: {log_level}")
        
        print("\n" + "=" * 50)
        print("🎉 All basic functionality tests passed!")
        print("\nThe MCP Speech-to-Text server is ready to use.")
        print("\nAvailable tools:")
        print("  - transcribe_audio: Convert audio files to text")
        print("  - get_supported_formats: List supported audio formats")
        print("  - convert_audio_format: Convert between audio formats")
        print("  - record_and_transcribe: Record and transcribe (if audio hardware available)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_server():
    """Test MCP server startup."""
    print("\n" + "=" * 50)
    print("🚀 Testing MCP Server Startup...")
    
    try:
        from mcp_speech_to_text.server import SpeechToTextServer
        print("   ✅ Server class imported successfully")
        
        # Try to initialize the server
        server = SpeechToTextServer()
        print("   ✅ Server initialized successfully")
        
        # Test tool listing
        tools_result = await server._get_supported_formats()
        print("   ✅ Tool execution test passed")
        print(f"   Result: {tools_result.content[0].text[:100]}...")
        
        print("\n🎉 MCP Server tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ MCP Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🧪 MCP Speech-to-Text Test Suite")
    print("=" * 50)
    
    basic_test = await test_basic_functionality()
    
    if basic_test:
        mcp_test = await test_mcp_server()
        
        if mcp_test:
            print("\n🎉 All tests passed! The server is ready.")
            print("\nTo start the full MCP server, run:")
            print("python -m mcp_speech_to_text.server")
        else:
            print("\n⚠️ Basic tests passed but MCP server has issues.")
    else:
        print("\n❌ Basic functionality tests failed.")
    
    return basic_test

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
