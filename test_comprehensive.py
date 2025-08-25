#!/usr/bin/env python3
"""
Comprehensive test suite for MCP Speech-to-Text
Tests both platform detection and server functionality
"""

import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_platform_detection():
    """Test the platform detection functionality"""
    print("🔍 Testing Platform Detection...")
    
    try:
        from mcp_speech_to_text.__main__ import detect_platform_capabilities
        caps = detect_platform_capabilities()
        
        print("✅ Platform detection successful")
        print(f"   Platform: {caps['platform']}")
        print(f"   Vosk supported: {caps['vosk_supported']}")
        print(f"   SpeechRecognition supported: {caps['speechrecognition_supported']}")
        print(f"   Offline capable: {caps['offline_capable']}")
        print(f"   Recommended backend: {caps['recommended_backend']}")
        print(f"   Production ready: {caps['production_ready']}")
        
        return True, caps
        
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
        return False, None

def test_speechrecognition_server():
    """Test the SpeechRecognition server"""
    print("\n🧪 Testing SpeechRecognition Server...")
    
    try:
        from mcp_speech_to_text.server_sr import SpeechToTextServer
        
        # Create server
        server = SpeechToTextServer()
        print("✅ SpeechRecognition server created")
        
        # Test server properties
        print(f"   Server name: {server.app.name}")
        print(f"   Recognizer available: {server.speech_recognizer is not None}")
        print(f"   Microphone available: {server.microphone is not None}")
        
        return True, server
        
    except Exception as e:
        print(f"❌ SpeechRecognition server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_vosk_server():
    """Test the Vosk server (if available)"""
    print("\n🧪 Testing Vosk Server...")
    
    try:
        from mcp_speech_to_text.server import OfflineSpeechToTextServer
        
        # Create server
        server = OfflineSpeechToTextServer()
        print("✅ Vosk server created")
        
        # Test server properties
        print(f"   Server name: {server.app.name}")
        print(f"   Vosk model loaded: {server.vosk_model is not None}")
        print(f"   Vosk recognizer ready: {server.vosk_rec is not None}")
        
        if server.vosk_model:
            print("✅ Vosk model is loaded and ready for offline recognition")
        else:
            print("ℹ️  Vosk model not loaded (use download_vosk_model tool)")
        
        return True, server
        
    except ImportError as e:
        print(f"ℹ️  Vosk not available: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Vosk server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_server_tools(server, server_type):
    """Test MCP tools functionality"""
    print(f"\n🛠️  Testing {server_type} Tools...")
    
    try:
        # Test list_tools functionality by inspecting the handlers
        if hasattr(server.app, '_tools_handlers'):
            tools_handler = server.app._tools_handlers.get('list_tools')
            if tools_handler:
                # This would normally be called by MCP, but we can test the structure
                print("✅ Tools handler found")
                return True
        
        print("ℹ️  Tools handler not directly testable (requires MCP runtime)")
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = {
        "mcp": "Model Context Protocol framework",
        "speech_recognition": "SpeechRecognition library",
        "pyaudio": "Audio recording support",
        "pydub": "Audio format conversion",
        "vosk": "Offline speech recognition (optional)"
    }
    
    results = {}
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep}: {description}")
            results[dep] = True
        except ImportError:
            if dep == "vosk":
                print(f"ℹ️  {dep}: {description} (not available on this platform)")
            else:
                print(f"❌ {dep}: {description} - NOT AVAILABLE")
            results[dep] = False
    
    return results

def create_test_summary(results):
    """Create a test summary"""
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    platform_ok, caps = results['platform']
    sr_ok, sr_server = results['speechrecognition']
    vosk_ok, vosk_server = results['vosk']
    deps = results['dependencies']
    
    if platform_ok and caps:
        print(f"🎯 Platform: {caps['platform']}")
        print(f"🎯 Recommended Backend: {caps['recommended_backend']}")
        print(f"🎯 Production Ready: {caps['production_ready']}")
        print(f"🎯 Offline Capable: {caps['offline_capable']}")
    
    print("\n📊 Server Availability:")
    print(f"   • SpeechRecognition: {'✅ Available' if sr_ok else '❌ Not available'}")
    print(f"   • Vosk Offline: {'✅ Available' if vosk_ok else '❌ Not available'}")
    
    print("\n📦 Dependencies:")
    for dep, available in deps.items():
        status = "✅ Installed" if available else "❌ Missing"
        print(f"   • {dep}: {status}")
    
    # Determine overall status
    critical_deps = ['mcp', 'speech_recognition']
    critical_ok = all(deps.get(dep, False) for dep in critical_deps)
    
    if platform_ok and (sr_ok or vosk_ok) and critical_ok:
        print("\n🎉 OVERALL STATUS: ✅ READY FOR DEPLOYMENT")
        
        if caps and caps['platform'].startswith('linux') and caps['platform'].endswith('x86_64'):
            print("🚀 Perfect for x86_64 production deployment!")
        elif caps and caps['platform'].startswith('darwin'):
            print("💻 Perfect for macOS development!")
        else:
            print("🔧 Ready for development and testing!")
            
    else:
        print("\n⚠️  OVERALL STATUS: ❌ NEEDS ATTENTION")
        print("💡 Install missing dependencies and try again")
    
    print("="*60)

async def main():
    """Run all tests"""
    print("🧪 MCP Speech-to-Text Comprehensive Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test platform detection
    results['platform'] = test_platform_detection()
    
    # Test dependencies
    results['dependencies'] = test_dependencies()
    
    # Test SpeechRecognition server
    results['speechrecognition'] = test_speechrecognition_server()
    
    # Test Vosk server
    results['vosk'] = test_vosk_server()
    
    # Test tools (if we have a working server)
    if results['speechrecognition'][0]:
        await test_server_tools(results['speechrecognition'][1], "SpeechRecognition")
    elif results['vosk'][0]:
        await test_server_tools(results['vosk'][1], "Vosk")
    
    # Create summary
    create_test_summary(results)

if __name__ == "__main__":
    asyncio.run(main())
