#!/usr/bin/env python3
"""
Test script for MCP Speech-to-Text server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_speech_to_text.server import SpeechToTextServer

async def test_server():
    """Test the MCP server functionality."""
    
    print("Testing MCP Speech-to-Text Server...")
    
    try:
        # Initialize server
        server = SpeechToTextServer()
        print("✓ Server initialized successfully")
        
        # Test get supported formats
        result = await server._get_supported_formats()
        print("✓ Supported formats tool works")
        print(f"  Result: {result.content[0].text}")
        
        print("\nAll tests passed! 🎉")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
