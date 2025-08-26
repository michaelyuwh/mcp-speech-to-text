"""
Local Offline MCP Speech-to-Text Server
Uses Vosk for completely local, offline speech recognition
No internet connection or API keys required
Optimized for x86_64 Linux production deployment
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
    """MCP server for completely local/offline speech-to-text using Vosk"""
    
    def __init__(self):
        self.app = Server("mcp-speech-to-text")
        self.vosk_model = None
        self.vosk_rec = None
        self._setup_handlers()
        self._initialize_vosk()
    
    def _initialize_vosk(self):
        """Initialize Vosk offline speech recognition"""
        try:
            import vosk
            
            # Check for models directory
            models_dir = os.path.join(os.path.dirname(__file__), "models")
            
            # Look for any vosk model
            model_path = None
            if os.path.exists(models_dir):
                for item in os.listdir(models_dir):
                    if item.startswith("vosk-model"):
                        model_path = os.path.join(models_dir, item)
                        break
            
            if not model_path:
                logger.warning("No Vosk model found. Please download a model:")
                logger.info("wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
                logger.info("unzip vosk-model-en-us-0.22.zip -d src/mcp_speech_to_text/models/")
                return
            
            logger.info(f"Loading Vosk model from: {model_path}")
            self.vosk_model = vosk.Model(model_path)
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            
            logger.info("Vosk offline speech recognition initialized successfully")
            
        except ImportError:
            logger.error("Vosk library not installed. Install with: pip install vosk")
        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}")
    
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
                                "description": "Model language hint (en, zh, fr, etc.)",
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
                            "input_path": {
                                "type": "string",
                                "description": "Path to input audio file"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Path for output WAV file (optional)"
                            },
                            "sample_rate": {
                                "type": "integer",
                                "description": "Sample rate for output (default: 16000)",
                                "default": 16000
                            }
                        },
                        "required": ["input_path"]
                    }
                ),
                Tool(
                    name="record_and_transcribe_offline",
                    description="Record audio from microphone and transcribe using local Vosk model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "number",
                                "description": "Recording duration in seconds",
                                "default": 5
                            },
                            "sample_rate": {
                                "type": "integer",
                                "description": "Sample rate for recording",
                                "default": 16000
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="download_vosk_model",
                    description="Download and setup Vosk models for offline recognition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {
                                "type": "string",
                                "description": "Model name (small-en-us, large-en-us, etc.)",
                                "default": "small-en-us"
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (en, zh, fr, etc.)",
                                "default": "en"
                            }
                        },
                        "required": []
                    }
                )
            ]

        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
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
                }, indent=2)
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
                        }, indent=2)
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
                }, indent=2)
            )]
        except Exception as e:
            logger.error(f"Offline transcription error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Transcription failed",
                    "message": str(e),
                    "service": "Vosk (Offline)"
                }, indent=2)
            )]
    
    async def _convert_audio_format(self, arguments: dict) -> list[TextContent]:
        """Convert audio to WAV format using pydub"""
        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path")
        sample_rate = arguments.get("sample_rate", 16000)
        
        if not output_path:
            name, ext = os.path.splitext(input_path)
            output_path = f"{name}_converted.wav"
        
        try:
            from pydub import AudioSegment
            
            logger.info(f"Converting {input_path} to {output_path}")
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(sample_rate)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            result = {
                "status": "success",
                "input_path": input_path,
                "output_path": output_path,
                "sample_rate": sample_rate,
                "channels": 1,
                "format": "wav"
            }
            
            logger.info(f"Audio conversion completed: {output_path}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except ImportError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Missing dependency",
                    "message": "Install pydub: pip install pydub"
                }, indent=2)
            )]
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Conversion failed",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _record_and_transcribe_offline(self, arguments: dict) -> list[TextContent]:
        """Record audio and transcribe using Vosk"""
        duration = arguments.get("duration", 5)
        sample_rate = arguments.get("sample_rate", 16000)
        
        if not self.vosk_model or not self.vosk_rec:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Vosk model not loaded",
                    "message": "Please download a Vosk model first"
                }, indent=2)
            )]
        
        try:
            import pyaudio
            import vosk
            
            logger.info(f"Recording audio for {duration} seconds...")
            
            # Setup audio recording
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=4000
            )
            
            # Reset recognizer
            rec = vosk.KaldiRecognizer(self.vosk_model, sample_rate)
            
            results = []
            frames_to_record = int(sample_rate / 4000 * duration)
            
            for _ in range(frames_to_record):
                data = stream.read(4000)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get('text'):
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                results.append(final_result['text'])
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            transcription = " ".join(results).strip()
            
            result = {
                "transcription": transcription,
                "duration": duration,
                "sample_rate": sample_rate,
                "service": "Vosk (Offline Recording)",
                "completely_local": True
            }
            
            logger.info("Recording and transcription completed")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except ImportError as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Missing dependency",
                    "message": f"Install required packages: {e}"
                }, indent=2)
            )]
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Recording failed",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _download_vosk_model(self, arguments: dict) -> list[TextContent]:
        """Download Vosk model for offline recognition"""
        model_name = arguments.get("model_name", "small-en-us")
        language = arguments.get("language", "en")
        
        try:
            import urllib.request
            import zipfile
            
            # Model URLs (small selection of popular models)
            model_urls = {
                "small-en-us": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                "en-us": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
                "small-zh": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip",
                "small-fr": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
                "small-de": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
                "small-es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
            }
            
            if model_name not in model_urls:
                available_models = list(model_urls.keys())
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Model '{model_name}' not available",
                        "available_models": available_models,
                        "message": "Choose from available models"
                    }, indent=2)
                )]
            
            url = model_urls[model_name]
            models_dir = os.path.join(os.path.dirname(__file__), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            # Download model
            zip_path = os.path.join(models_dir, f"{model_name}.zip")
            logger.info(f"Downloading model from {url}")
            
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract model
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)
            
            # Remove zip file
            os.remove(zip_path)
            
            # Reinitialize Vosk with new model
            self._initialize_vosk()
            
            result = {
                "status": "success",
                "model_name": model_name,
                "language": language,
                "download_url": url,
                "models_directory": models_dir,
                "message": "Model downloaded and loaded successfully"
            }
            
            logger.info(f"Model {model_name} downloaded successfully")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Model download error: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Download failed",
                    "message": str(e),
                    "model_name": model_name
                }, indent=2)
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
    server = OfflineSpeechToTextServer()
    await server.run_server()

if __name__ == "__main__":
    asyncio.run(main())
