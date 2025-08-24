#!/usr/bin/env python3
"""
Simple HTTP API wrapper for testing MCP Speech-to-Text tools
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add src to path
sys.path.insert(0, '/app/src' if os.path.exists('/app/src') else 'src')

from mcp_speech_to_text.server import SpeechToTextServer

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP tools."""
    
    def __init__(self, *args, mcp_server=None, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._send_response(200, {'status': 'healthy', 'message': 'MCP Speech-to-Text server is running'})
        elif self.path == '/tools':
            asyncio.run(self._handle_list_tools())
        else:
            self._send_response(404, {'error': 'Not found'})
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/tools/call':
            asyncio.run(self._handle_tool_call())
        else:
            self._send_response(404, {'error': 'Not found'})
    
    async def _handle_list_tools(self):
        """Handle tool listing."""
        try:
            # Create a mock list tools result
            tools = [
                {
                    "name": "transcribe_audio",
                    "description": "Transcribe audio file to text using Whisper model",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "audio_file_path": {"type": "string", "description": "Path to audio file"},
                            "language": {"type": "string", "description": "Language code (optional)"},
                            "model_size": {"type": "string", "description": "Model size (optional)"}
                        },
                        "required": ["audio_file_path"]
                    }
                },
                {
                    "name": "get_supported_formats",
                    "description": "Get list of supported audio formats",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "record_and_transcribe",
                    "description": "Record audio from microphone and transcribe to text",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number", "description": "Recording duration in seconds"},
                            "language": {"type": "string", "description": "Language code (optional)"}
                        },
                        "required": ["duration"]
                    }
                },
                {
                    "name": "convert_audio_format",
                    "description": "Convert audio file to a different format",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input_file_path": {"type": "string", "description": "Input file path"},
                            "output_file_path": {"type": "string", "description": "Output file path"},
                            "output_format": {"type": "string", "description": "Target format"}
                        },
                        "required": ["input_file_path", "output_file_path", "output_format"]
                    }
                }
            ]
            self._send_response(200, {"tools": tools})
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    async def _handle_tool_call(self):
        """Handle tool execution."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            tool_name = request_data.get('name')
            arguments = request_data.get('arguments', {})
            
            if tool_name == 'get_supported_formats':
                result = await self.mcp_server._get_supported_formats()
            elif tool_name == 'transcribe_audio':
                result = await self.mcp_server._transcribe_audio(**arguments)
            elif tool_name == 'record_and_transcribe':
                result = await self.mcp_server._record_and_transcribe(**arguments)
            elif tool_name == 'convert_audio_format':
                result = await self.mcp_server._convert_audio_format(**arguments)
            else:
                self._send_response(400, {'error': f'Unknown tool: {tool_name}'})
                return
            
            # Convert CallToolResult to dict
            response = {
                'content': [{'type': content.type, 'text': content.text} for content in result.content],
                'isError': getattr(result, 'isError', False)
            }
            
            self._send_response(200, response)
            
        except Exception as e:
            self._send_response(500, {'error': str(e), 'traceback': str(e.__traceback__)})
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log message to reduce noise."""
        print(f"[{self.address_string()}] {format % args}")

async def main():
    """Start the HTTP server."""
    print("🚀 Starting MCP Speech-to-Text HTTP Test Server...")
    print("=" * 50)
    
    try:
        # Initialize MCP server
        mcp_server = SpeechToTextServer()
        print("✅ MCP Server initialized")
        
        # Create HTTP server
        def handler(*args, **kwargs):
            MCPHandler(*args, mcp_server=mcp_server, **kwargs)
        
        port = int(os.getenv('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), handler)
        
        print(f"🌐 HTTP server starting on port {port}")
        print(f"📡 Health check: http://localhost:{port}/health")
        print(f"🛠️ List tools: http://localhost:{port}/tools")
        print(f"⚡ Call tools: POST http://localhost:{port}/tools/call")
        print("")
        print("Example tool call:")
        print("curl -X POST http://localhost:8000/tools/call \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"name\": \"get_supported_formats\", \"arguments\": {}}'")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
