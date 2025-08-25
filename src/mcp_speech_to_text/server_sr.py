"""
Local MCP Speech-to-Text Server
Uses SpeechRecognition library with multiple engines
Supports both offline and online recognition
"""

import asyncio
import json
import logging
import os
import tempfile
import wave
from typing import Any, Optional, List
import io

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest, 
    CallToolResult, 
    ListToolsRequest, 
    ListToolsResult, 
    Tool,
    TextContent,
    JSONRPCMessage,
    ErrorData,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechToTextServer:
    """MCP server for speech-to-text using SpeechRecognition library"""
    
    def __init__(self):
        self.app = Server("mcp-speech-to-text")
        self.speech_recognizer = None
        self.microphone = None
        self._setup_handlers()
        self._initialize_speech_recognition()
    
    def _initialize_speech_recognition(self):
        """Initialize SpeechRecognition library"""
        try:
            import speech_recognition as sr
            
            self.speech_recognizer = sr.Recognizer()
            
            # Try to initialize microphone
            try:
                self.microphone = sr.Microphone()
                # Adjust for ambient noise
                with self.microphone as source:
                    self.speech_recognizer.adjust_for_ambient_noise(source)
                
                mic_list = sr.Microphone.list_microphone_names()
                logger.info(f"Microphone initialized. Found {len(mic_list)} microphone(s)")
                
            except Exception as e:
                logger.warning(f"Could not initialize microphone: {e}")
                logger.info("File-based transcription will still work")
            
            logger.info("SpeechRecognition initialized successfully")
            logger.info("Available engines: Google (default), Sphinx (offline), macOS built-in")
            
        except ImportError:
            logger.error("SpeechRecognition library not installed. Install with: uv add SpeechRecognition")
        except Exception as e:
            logger.error(f"Failed to initialize SpeechRecognition: {e}")
    
    def _setup_handlers(self):
        """Setup MCP message handlers"""
        
        @self.app.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available speech-to-text tools"""
            return [
                Tool(
                    name="get_supported_engines",
                    description="Get list of supported speech recognition engines",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="transcribe_audio_file",
                    description="Transcribe audio file to text using specified engine",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the audio file"
                            },
                            "engine": {
                                "type": "string",
                                "enum": ["google", "sphinx", "wit", "azure", "houndify", "ibm"],
                                "default": "google",
                                "description": "Speech recognition engine to use"
                            },
                            "language": {
                                "type": "string",
                                "default": "en-US",
                                "description": "Language code (e.g., 'en-US', 'es-ES')"
                            }
                        },
                        "required": ["file_path"]
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
                                "default": 5,
                                "description": "Recording duration in seconds"
                            },
                            "engine": {
                                "type": "string",
                                "enum": ["google", "sphinx", "wit", "azure", "houndify", "ibm"],
                                "default": "google",
                                "description": "Speech recognition engine to use"
                            },
                            "language": {
                                "type": "string",
                                "default": "en-US",
                                "description": "Language code"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="test_microphone",
                    description="Test microphone functionality and list available devices",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="convert_audio_format",
                    description="Convert audio file to supported format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_path": {
                                "type": "string",
                                "description": "Path to input audio file"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Path for output file (optional, auto-generated if not provided)"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["wav", "flac"],
                                "default": "wav",
                                "description": "Output format"
                            }
                        },
                        "required": ["input_path"]
                    }
                )
            ]

        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                if name == "get_supported_engines":
                    return await self._get_supported_engines()
                elif name == "transcribe_audio_file":
                    return await self._transcribe_audio_file(arguments)
                elif name == "record_and_transcribe":
                    return await self._record_and_transcribe(arguments)
                elif name == "test_microphone":
                    return await self._test_microphone()
                elif name == "convert_audio_format":
                    return await self._convert_audio_format(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool '{name}': {e}")
                raise Exception(f"Internal error: {str(e)}")
    
    async def _get_supported_engines(self) -> list[TextContent]:
        """Get supported speech recognition engines"""
        engines = {
            "available_engines": [
                {
                    "name": "google",
                    "description": "Google Web Speech API (requires internet)",
                    "free": True,
                    "languages": "100+ languages supported",
                    "accuracy": "Very High",
                    "offline": False
                },
                {
                    "name": "sphinx",
                    "description": "CMU Sphinx (offline, but requires additional setup)",
                    "free": True,
                    "languages": "Limited language support",
                    "accuracy": "Moderate",
                    "offline": True
                }
            ],
            "default_engine": "google",
            "recommendation": "Use 'google' for best results with internet, 'sphinx' for offline (requires PocketSphinx install)",
            "note": "Some engines require API keys or additional packages"
        }
        
        return [TextContent(type="text", text=json.dumps(engines, indent=2))]
    
    async def _transcribe_audio_file(self, arguments: dict) -> list[TextContent]:
        """Transcribe audio file using SpeechRecognition"""
        
        if not self.speech_recognizer:
            return [TextContent(
                type="text", 
                text=json.dumps({
                    "error": "SpeechRecognition not initialized",
                    "message": "Install with: uv add SpeechRecognition"
                })
            )]
        
        file_path = arguments.get("file_path")
        engine = arguments.get("engine", "google")
        language = arguments.get("language", "en-US")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            import speech_recognition as sr
            
            logger.info(f"Transcribing audio file: {file_path} using {engine} engine")
            
            # Load audio file
            with sr.AudioFile(file_path) as source:
                audio = self.speech_recognizer.record(source)
            
            # Choose recognition method based on engine
            text = ""
            if engine == "google":
                text = self.speech_recognizer.recognize_google(audio, language=language)
            elif engine == "sphinx":
                text = self.speech_recognizer.recognize_sphinx(audio, language=language)
            elif engine == "wit":
                # Requires WIT_AI_KEY
                text = self.speech_recognizer.recognize_wit(audio)
            else:
                raise ValueError(f"Unsupported engine: {engine}")
            
            result = {
                "transcription": text,
                "language": language,
                "engine": engine,
                "file_path": file_path,
                "status": "success"
            }
            
            logger.info(f"Transcription completed successfully using {engine}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except sr.UnknownValueError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "No speech detected",
                    "message": "Could not understand audio",
                    "engine": engine
                })
            )]
        except sr.RequestError as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Service error",
                    "message": f"Could not request results from {engine} service: {e}",
                    "engine": engine
                })
            )]
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Transcription failed",
                    "message": str(e),
                    "engine": engine
                })
            )]
    
    async def _record_and_transcribe(self, arguments: dict) -> list[TextContent]:
        """Record audio from microphone and transcribe"""
        
        if not self.speech_recognizer or not self.microphone:
            return [TextContent(
                type="text", 
                text=json.dumps({
                    "error": "Microphone not available",
                    "message": "Could not initialize microphone"
                })
            )]
        
        duration = arguments.get("duration", 5)
        engine = arguments.get("engine", "google")
        language = arguments.get("language", "en-US")
        
        try:
            import speech_recognition as sr
            
            logger.info(f"Recording audio for {duration} seconds...")
            
            # Record audio
            with self.microphone as source:
                logger.info("Recording... Speak now!")
                audio = self.speech_recognizer.listen(source, timeout=duration)
            
            logger.info(f"Recording complete. Transcribing using {engine}...")
            
            # Transcribe
            text = ""
            if engine == "google":
                text = self.speech_recognizer.recognize_google(audio, language=language)
            elif engine == "sphinx":
                text = self.speech_recognizer.recognize_sphinx(audio, language=language)
            else:
                raise ValueError(f"Unsupported engine for recording: {engine}")
            
            result = {
                "transcription": text,
                "language": language,
                "engine": engine,
                "duration": duration,
                "status": "success"
            }
            
            logger.info("Recording and transcription completed successfully")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except sr.WaitTimeoutError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Recording timeout",
                    "message": f"No audio detected within {duration} seconds"
                })
            )]
        except sr.UnknownValueError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "No speech detected",
                    "message": "Could not understand the recorded audio"
                })
            )]
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Recording failed",
                    "message": str(e)
                })
            )]
    
    async def _test_microphone(self) -> list[TextContent]:
        """Test microphone functionality"""
        try:
            import speech_recognition as sr
            
            mic_list = sr.Microphone.list_microphone_names()
            
            result = {
                "microphone_available": self.microphone is not None,
                "total_microphones": len(mic_list),
                "microphone_list": mic_list[:10],  # Show first 10
                "default_microphone": mic_list[0] if mic_list else None,
                "status": "success"
            }
            
            if self.microphone:
                result["message"] = "Microphone is ready for recording"
            else:
                result["message"] = "No microphone available"
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Microphone test failed",
                    "message": str(e)
                })
            )]
    
    async def _convert_audio_format(self, arguments: dict) -> list[TextContent]:
        """Convert audio file format (placeholder - requires pydub)"""
        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path")
        format_type = arguments.get("format", "wav")
        
        try:
            # For now, just return info about SpeechRecognition supported formats
            import speech_recognition as sr
            
            # SpeechRecognition supports these formats directly
            supported_formats = [".wav", ".aiff", ".flac"]
            
            if not output_path:
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_converted.{format_type}"
            
            result = {
                "note": "Basic format conversion requires pydub",
                "supported_by_speechrecognition": supported_formats,
                "input_path": input_path,
                "output_path": output_path,
                "requested_format": format_type,
                "message": "For best compatibility, use WAV, AIFF, or FLAC files directly"
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Format info failed",
                    "message": str(e)
                })
            )]

    async def run_server(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-speech-to-text",
                    server_version="1.0.0",
                    capabilities=self.app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

# Entry point for running the server
async def main():
    """Main entry point"""
    server = SpeechToTextServer()
    await server.run_server()

if __name__ == "__main__":
    asyncio.run(main())
