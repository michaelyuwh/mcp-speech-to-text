#!/usr/bin/env python3
"""
Example usage of MCP Speech-to-Text server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def example_usage():
    """Example of how to use the MCP Speech-to-Text tools"""
    
    print("MCP Speech-to-Text Example Usage")
    print("=" * 40)
    
    # Example 1: Get supported formats
    print("\n1. Getting supported audio formats:")
    print("Tool: get_supported_formats")
    print("Parameters: {}")
    print("Expected result: List of supported audio file extensions")
    
    # Example 2: Transcribe audio file
    print("\n2. Transcribing an audio file:")
    print("Tool: transcribe_audio")
    print("Parameters:")
    example_params = {
        "audio_file_path": "/path/to/audio/file.wav",
        "language": "en",  # optional
        "model_size": "base"  # optional
    }
    print(json.dumps(example_params, indent=2))
    print("Expected result: Transcribed text with metadata")
    
    # Example 3: Record and transcribe
    print("\n3. Recording and transcribing:")
    print("Tool: record_and_transcribe")
    print("Parameters:")
    record_params = {
        "duration": 10,  # record for 10 seconds
        "language": "auto"  # auto-detect language
    }
    print(json.dumps(record_params, indent=2))
    print("Expected result: Transcribed text from microphone recording")
    
    # Example 4: Convert audio format
    print("\n4. Converting audio format:")
    print("Tool: convert_audio_format")
    print("Parameters:")
    convert_params = {
        "input_file_path": "/path/to/input/audio.mp3",
        "output_file_path": "/path/to/output/audio.wav",
        "output_format": "wav"
    }
    print(json.dumps(convert_params, indent=2))
    print("Expected result: Converted audio file with metadata")
    
    print("\n" + "=" * 40)
    print("For n8n integration:")
    print("1. Use HTTP Request nodes to call the MCP server")
    print("2. Configure the server endpoint (e.g., http://localhost:8000)")
    print("3. Pass the tool name and parameters in the request body")
    print("4. Process the returned transcription in your workflow")

if __name__ == "__main__":
    asyncio.run(example_usage())
