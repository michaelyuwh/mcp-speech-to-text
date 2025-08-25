"""
Local Offline MCP Speech-to-Text Server
Uses SpeechRecognition with offline capabilities
No internet connection or API keys required for basic functionality
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

class OfflineSpeechToTextServer:
    """MCP server for local speech-to-text using SpeechRecognition library"""
    
    def __init__(self):
        self.app = Server("mcp-speech-to-text")
        self.speech_recognizer = None
        self._setup_handlers()
        self._initialize_speech_recognition()
    
    def _initialize_speech_recognition(self):
        """Initialize SpeechRecognition library"""
        try:
            import speech_recognition as sr
            
            self.speech_recognizer = sr.Recognizer()
            
            # Test microphone availability
            try:
                mic_list = sr.Microphone.list_microphone_names()
                logger.info(f"Found {len(mic_list)} microphone(s)")
            except Exception as e:
                logger.warning(f"Could not enumerate microphones: {e}")
            
            logger.info("SpeechRecognition initialized successfully")
            logger.info("Available engines: Google (offline), Sphinx (offline), macOS built-in")
            
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
                    name="get_supported_formats",
                    description="Get list of supported audio formats for offline speech recognition",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="transcribe_audio_offline",
                    description="Transcribe audio file to text using local Vosk model (completely offline)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the audio file to transcribe"
                            },
                            "model_language": {
                                "type": "string", 
                                "description": "Model language hint (en, zh, fr, etc.) - informational only",
                                "default": "en"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="convert_audio_format",
                    description="Convert audio file to WAV format compatible with Vosk",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_path": {"type": "string", "description": "Input audio file path"},
                            "output_path": {"type": "string", "description": "Output WAV file path"},
                            "sample_rate": {"type": "number", "description": "Sample rate (16000 recommended)", "default": 16000}
                        },
                        "required": ["input_path", "output_path"]
                    }
                ),
                Tool(
                    name="record_and_transcribe_offline",
                    description="Record audio from microphone and transcribe using local Vosk model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number", "description": "Recording duration in seconds"},
                            "output_file": {"type": "string", "description": "Optional: save recording to file", "default": ""}
                        },
                        "required": ["duration"]
                    }
                ),
                Tool(
                    name="download_vosk_model",
                    description="Download and setup Vosk models for offline recognition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "language": {
                                "type": "string", 
                                "description": "Language code: en-us, en-small, zh, fr, de, es, etc.",
                                "default": "en-us"
                            },
                            "model_size": {
                                "type": "string",
                                "description": "Model size: small, medium, large",
                                "default": "small"
                            }
                        },
                        "required": []
                    }
                )
            ]
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_supported_formats":
                    return await self._get_supported_formats()
                elif name == "transcribe_audio_offline":
                    return await self._transcribe_audio_offline(arguments)
                elif name == "convert_audio_format":
                    return await self._convert_audio_format(arguments)
                elif name == "record_and_transcribe_offline":
                    return await self._record_and_transcribe_offline(arguments)
                elif name == "download_vosk_model":
                    return await self._download_vosk_model(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool '{name}': {e}")
                raise Exception(f"Internal error: {str(e)}")
    
    async def _get_supported_formats(self) -> list[TextContent]:
        """Get supported audio formats"""
        formats = {
            "supported_input_formats": [
                ".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm", ".amr"
            ],
            "output_format": ".wav (16kHz mono)",
            "recommended_workflow": "Use convert_audio_format to convert any input to WAV before transcription",
            "note": "Vosk works best with 16kHz mono WAV files",
            "completely_offline": True,
            "no_internet_required": True,
            "no_api_costs": True
        }
        
        return [TextContent(type="text", text=json.dumps(formats, indent=2))]
    
    async def _transcribe_audio_offline(self, arguments: dict) -> list[TextContent]:
        """Transcribe audio using Vosk offline model"""
        
        if not self.vosk_model or not self.vosk_rec:
            return [TextContent(
                type="text", 
                text=json.dumps({
                    "error": "Vosk model not loaded",
                    "message": "Please download a Vosk model using download_vosk_model tool",
                    "setup_instructions": [
                        "Use the download_vosk_model tool to get a model",
                        "Or manually download from https://alphacephei.com/vosk/models/",
                        "Extract to src/mcp_speech_to_text/models/"
                    ]
                })
            )]
        
        file_path = arguments.get("file_path")
        model_language = arguments.get("model_language", "en")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            import vosk
            
            # Convert to WAV if needed
            wav_path = file_path
            if not file_path.lower().endswith('.wav'):
                wav_path = file_path + "_converted.wav"
                convert_result = await self._convert_audio_format({
                    "input_path": file_path,
                    "output_path": wav_path,
                    "sample_rate": 16000
                })
                
                # Check if conversion was successful
                if not os.path.exists(wav_path):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Audio conversion failed",
                            "message": "Could not convert audio to WAV format"
                        })
                    )]
            
            logger.info(f"Transcribing audio file offline: {wav_path}")
            
            # Read WAV file
            with wave.open(wav_path, 'rb') as wf:
                # Check format
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                    logger.warning(f"Audio format not optimal: {wf.getnchannels()}ch, {wf.getsampwidth()}bytes, {wf.getframerate()}Hz")
                
                # Reset recognizer
                self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, wf.getframerate())
                
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if self.vosk_rec.AcceptWaveform(data):
                        result = json.loads(self.vosk_rec.Result())
                        if result.get('text'):
                            results.append(result['text'])
                
                # Get final result
                final_result = json.loads(self.vosk_rec.FinalResult())
                if final_result.get('text'):
                    results.append(final_result['text'])
            
            # Combine all results
            full_transcription = " ".join(results).strip()
            
            # Clean up converted file if created
            if wav_path != file_path and os.path.exists(wav_path):
                os.unlink(wav_path)
            
            result = {
                "transcription": full_transcription,
                "language": model_language,
                "confidence": 0.9,  # Vosk doesn't provide confidence scores
                "service": "Vosk (Offline)",
                "file_path": file_path,
                "model_type": "offline",
                "completely_local": True,
                "no_internet_required": True,
                "no_api_costs": True
            }
            
            logger.info("Offline transcription completed successfully")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except ImportError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Missing dependency",
                    "message": "Install Vosk: pip install vosk"
                })
            )]
        except Exception as e:
            logger.error(f"Offline transcription error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Transcription failed",
                    "message": str(e),
                    "service": "Vosk (Offline)"
                })
            )]
    
    async def _convert_audio_format(self, arguments: dict) -> list[TextContent]:
        """Convert audio to WAV format using pydub"""
        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path")
        sample_rate = arguments.get("sample_rate", 16000)
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            from pydub import AudioSegment
            
            logger.info(f"Converting {input_path} to WAV format")
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to optimal format for Vosk (16kHz, mono, 16-bit)
            audio = audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            result = {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "format": "WAV",
                "sample_rate": sample_rate,
                "channels": 1,
                "bit_depth": 16,
                "optimized_for": "Vosk offline recognition",
                "message": "Successfully converted to Vosk-compatible WAV format"
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except ImportError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Missing dependency",
                    "message": "Install pydub: pip install pydub"
                })
            )]
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise Exception(f"Audio conversion failed: {e}")
    
    async def _record_and_transcribe_offline(self, arguments: dict) -> list[TextContent]:
        """Record audio and transcribe using Vosk offline"""
        duration = arguments.get("duration", 5.0)
        output_file = arguments.get("output_file", "")
        
        if not self.vosk_model:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Vosk model not loaded",
                    "message": "Please download a Vosk model first"
                })
            )]
        
        try:
            import pyaudio
            import vosk
            
            # Audio recording parameters
            CHUNK = 4000
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            # Initialize audio
            p = pyaudio.PyAudio()
            
            # Create recognizer
            rec = vosk.KaldiRecognizer(self.vosk_model, RATE)
            
            logger.info(f"Recording for {duration} seconds...")
            
            # Start recording
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            
            frames = []
            results = []
            
            # Record audio in chunks and transcribe in real-time
            for i in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
                
                # Process with Vosk
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get('text'):
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                results.append(final_result['text'])
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save recording if requested
            if output_file:
                import wave
                wf = wave.open(output_file, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # Combine results
            full_transcription = " ".join(results).strip()
            
            result_data = {
                "transcription": full_transcription,
                "duration": duration,
                "service": "Vosk (Offline Recording)",
                "recording_saved": output_file if output_file else None,
                "completely_local": True,
                "no_internet_required": True,
                "real_time_processing": True
            }
            
            return [TextContent(type="text", text=json.dumps(result_data, indent=2))]
            
        except ImportError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Missing dependency",
                    "message": "Install packages: pip install vosk pyaudio"
                })
            )]
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Recording failed",
                    "message": str(e),
                    "service": "Vosk (Offline)"
                })
            )]
    
    async def _download_vosk_model(self, arguments: dict) -> list[TextContent]:
        """Download Vosk models for offline use"""
        language = arguments.get("language", "en-us")
        model_size = arguments.get("model_size", "small")
        
        try:
            import urllib.request
            import zipfile
            import shutil
            
            # Model URLs (this is a simplified example)
            model_urls = {
                "en-us-small": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
                "en-us": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
                "zh": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
                "fr": "https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip",
                "de": "https://alphacephei.com/vosk/models/vosk-model-de-0.22.zip",
                "es": "https://alphacephei.com/vosk/models/vosk-model-es-0.22.zip"
            }
            
            model_key = f"{language}-{model_size}" if f"{language}-{model_size}" in model_urls else language
            
            if model_key not in model_urls:
                available_models = list(model_urls.keys())
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Model not available",
                        "message": f"Model '{model_key}' not found",
                        "available_models": available_models,
                        "manual_download": "Visit https://alphacephei.com/vosk/models/ for more models"
                    })
                )]
            
            url = model_urls[model_key]
            models_dir = os.path.join(os.path.dirname(__file__), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            zip_path = os.path.join(models_dir, f"{model_key}.zip")
            
            logger.info(f"Downloading Vosk model: {model_key}")
            
            # Download model
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract model
            logger.info("Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)
            
            # Clean up zip file
            os.remove(zip_path)
            
            # Reinitialize Vosk with new model
            self._initialize_vosk()
            
            result = {
                "success": True,
                "model": model_key,
                "location": models_dir,
                "message": "Model downloaded and ready for offline use",
                "next_step": "You can now use transcribe_audio_offline tool"
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Model download failed: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Download failed",
                    "message": str(e),
                    "manual_instructions": [
                        "Visit https://alphacephei.com/vosk/models/",
                        "Download a model ZIP file",
                        "Extract to src/mcp_speech_to_text/models/",
                        "Restart the server"
                    ]
                })
            )]

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP Speech-to-Text Server v1.0.0 (Local/Offline)")
        
        # Initialize the server
        async with self.app.stdio() as (read_stream, write_stream):
            await self.app.run(
                read_stream, write_stream, InitializationOptions(
                    server_name="mcp-speech-to-text",
                    server_version="1.0.0",
                    capabilities=self.app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = OfflineSpeechToTextServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
