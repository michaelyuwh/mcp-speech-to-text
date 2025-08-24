"""
Unit tests for MCP Speech-to-Text server
"""

import pytest
import tempfile
import os
from pathlib import Path
import asyncio

# Mock the imports that might not be available in test environment
import sys
from unittest.mock import MagicMock, patch

# Mock the external dependencies
sys.modules['whisper'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()
sys.modules['pydub'] = MagicMock()
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.models'] = MagicMock()
sys.modules['mcp.server.stdio'] = MagicMock()
sys.modules['mcp.types'] = MagicMock()

class TestSpeechToTextServer:
    """Test cases for SpeechToTextServer"""
    
    @pytest.fixture
    def temp_audio_file(self):
        """Create a temporary audio file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Write some dummy audio data
            f.write(b'\x00' * 1024)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_supported_formats(self):
        """Test that supported formats are correctly defined"""
        from mcp_speech_to_text.server import SpeechToTextServer
        
        with patch('mcp_speech_to_text.server.whisper') as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            server = SpeechToTextServer()
            
            expected_formats = [
                ".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"
            ]
            assert server.supported_formats == expected_formats
    
    @pytest.mark.asyncio
    async def test_get_supported_formats_tool(self):
        """Test the get_supported_formats tool"""
        from mcp_speech_to_text.server import SpeechToTextServer
        
        with patch('mcp_speech_to_text.server.whisper') as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            server = SpeechToTextServer()
            
            result = await server._get_supported_formats()
            
            assert result is not None
            assert len(result.content) > 0
            assert "supported_formats" in result.content[0].text
    
    def test_initialization(self):
        """Test server initialization"""
        from mcp_speech_to_text.server import SpeechToTextServer
        
        with patch('mcp_speech_to_text.server.whisper') as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            
            server = SpeechToTextServer()
            
            assert server.model_size == "base"  # default value
            assert server.default_language == "auto"  # default value
            assert server.whisper_model is not None
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_file_not_found(self):
        """Test transcribe_audio with non-existent file"""
        from mcp_speech_to_text.server import SpeechToTextServer
        
        with patch('mcp_speech_to_text.server.whisper') as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            server = SpeechToTextServer()
            
            with pytest.raises(FileNotFoundError):
                await server._transcribe_audio("/non/existent/file.wav")
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_unsupported_format(self, temp_audio_file):
        """Test transcribe_audio with unsupported format"""
        from mcp_speech_to_text.server import SpeechToTextServer
        
        with patch('mcp_speech_to_text.server.whisper') as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            server = SpeechToTextServer()
            
            # Rename to unsupported format
            unsupported_file = temp_audio_file.replace('.wav', '.xyz')
            os.rename(temp_audio_file, unsupported_file)
            
            try:
                with pytest.raises(ValueError, match="Unsupported audio format"):
                    await server._transcribe_audio(unsupported_file)
            finally:
                if os.path.exists(unsupported_file):
                    os.unlink(unsupported_file)

if __name__ == "__main__":
    pytest.main([__file__])
