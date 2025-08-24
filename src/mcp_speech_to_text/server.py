#!/usr/bin/env python3
"""
MCP Speech-to-Text Server

A Model Context Protocol server that provides Speech-to-Text functionality
using OpenAI Whisper and other speech recognition engines.
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import whisper
except ImportError:
    whisper = None

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechToTextServer:
    """MCP Server for Speech-to-Text functionality."""
    
    def __init__(self):
        self.server = Server("mcp-speech-to-text")
        self.whisper_model = None
        self.model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "auto")
        self.supported_formats = [
            ".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"
        ]
        
        # Initialize Whisper model
        self._load_whisper_model()
        
        # Register handlers
        self._register_handlers()
    
    def _load_whisper_model(self):
        """Load the Whisper model."""
        if whisper is None:
            logger.error("Whisper is not installed. Please install it: pip install openai-whisper")
            raise ImportError("Whisper not available")
            
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def _register_handlers(self):
        """Register MCP handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="transcribe_audio",
                        description="Transcribe audio file to text using Whisper model",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "audio_file_path": {
                                    "type": "string",
                                    "description": "Path to the audio file to transcribe"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Language code for transcription (optional, auto-detect if not specified)",
                                    "default": "auto"
                                },
                                "model_size": {
                                    "type": "string",
                                    "description": "Whisper model size to use",
                                    "enum": ["tiny", "base", "small", "medium", "large"],
                                    "default": "base"
                                }
                            },
                            "required": ["audio_file_path"]
                        }
                    ),
                    Tool(
                        name="record_and_transcribe",
                        description="Record audio from microphone and transcribe to text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "duration": {
                                    "type": "number",
                                    "description": "Recording duration in seconds",
                                    "minimum": 1,
                                    "maximum": 300
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Language code for transcription (optional)",
                                    "default": "auto"
                                }
                            },
                            "required": ["duration"]
                        }
                    ),
                    Tool(
                        name="get_supported_formats",
                        description="Get list of supported audio formats",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="convert_audio_format",
                        description="Convert audio file to a different format",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "input_file_path": {
                                    "type": "string",
                                    "description": "Path to the input audio file"
                                },
                                "output_file_path": {
                                    "type": "string",
                                    "description": "Path for the output audio file"
                                },
                                "output_format": {
                                    "type": "string",
                                    "description": "Target audio format",
                                    "enum": ["wav", "mp3", "m4a", "ogg", "flac"]
                                }
                            },
                            "required": ["input_file_path", "output_file_path", "output_format"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "transcribe_audio":
                    return await self._transcribe_audio(**arguments)
                elif name == "record_and_transcribe":
                    return await self._record_and_transcribe(**arguments)
                elif name == "get_supported_formats":
                    return await self._get_supported_formats()
                elif name == "convert_audio_format":
                    return await self._convert_audio_format(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _transcribe_audio(
        self, 
        audio_file_path: str, 
        language: str = "auto",
        model_size: str = None
    ) -> CallToolResult:
        """Transcribe audio file to text."""
        try:
            # Validate file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Check file format
            file_ext = Path(audio_file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {file_ext}")
            
            # Load different model if requested
            model = self.whisper_model
            if model_size and model_size != self.model_size:
                logger.info(f"Loading temporary model: {model_size}")
                model = whisper.load_model(model_size)
            
            # Transcribe audio
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Set language parameter
            lang_param = None if language == "auto" else language
            
            result = model.transcribe(
                audio_file_path,
                language=lang_param,
                verbose=False
            )
            
            # Extract transcription details
            text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            
            response_data = {
                "transcription": text,
                "detected_language": detected_language,
                "file_path": audio_file_path,
                "model_used": model_size or self.model_size
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=json.dumps(response_data, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def _record_and_transcribe(
        self, 
        duration: float, 
        language: str = "auto"
    ) -> CallToolResult:
        """Record audio from microphone and transcribe."""
        if sr is None or pyaudio is None:
            raise ImportError("Speech recognition libraries not available. Install: pip install speechrecognition pyaudio")
            
        try:
            # Initialize recognizer and microphone
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            # Adjust for ambient noise
            logger.info("Adjusting for ambient noise...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
            
            # Record audio
            logger.info(f"Recording for {duration} seconds...")
            with microphone as source:
                audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Save to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                with open(temp_path, "wb") as f:
                    f.write(audio.get_wav_data())
            
            try:
                # Transcribe using Whisper
                lang_param = None if language == "auto" else language
                result = self.whisper_model.transcribe(
                    temp_path,
                    language=lang_param,
                    verbose=False
                )
                
                text = result["text"].strip()
                detected_language = result.get("language", "unknown")
                
                response_data = {
                    "transcription": text,
                    "detected_language": detected_language,
                    "recording_duration": duration,
                    "model_used": self.model_size
                }
                
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=json.dumps(response_data, indent=2)
                    )]
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Recording and transcription failed: {e}")
            raise
    
    async def _get_supported_formats(self) -> CallToolResult:
        """Get list of supported audio formats."""
        response_data = {
            "supported_formats": self.supported_formats,
            "description": "List of audio file formats supported for transcription"
        }
        
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=json.dumps(response_data, indent=2)
            )]
        )
    
    async def _convert_audio_format(
        self, 
        input_file_path: str, 
        output_file_path: str, 
        output_format: str
    ) -> CallToolResult:
        """Convert audio file to different format."""
        if AudioSegment is None:
            raise ImportError("Pydub not available. Install: pip install pydub")
            
        try:
            # Validate input file
            if not os.path.exists(input_file_path):
                raise FileNotFoundError(f"Input file not found: {input_file_path}")
            
            # Load audio file
            logger.info(f"Converting {input_file_path} to {output_format}")
            audio = AudioSegment.from_file(input_file_path)
            
            # Export in new format
            audio.export(output_file_path, format=output_format)
            
            response_data = {
                "status": "success",
                "input_file": input_file_path,
                "output_file": output_file_path,
                "output_format": output_format,
                "file_size_mb": round(os.path.getsize(output_file_path) / (1024 * 1024), 2)
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=json.dumps(response_data, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise

async def main():
    """Main function to run the MCP server."""
    logger.info("Starting MCP Speech-to-Text Server v1.0.0")
    
    try:
        # Initialize server
        stt_server = SpeechToTextServer()
        
        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await stt_server.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="mcp-speech-to-text",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
