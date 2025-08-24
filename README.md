# MCP Speech-to-Text Server

A powerful Model Context Protocol (MCP) server that provides speech-to-text capabilities using OpenAI Whisper. Perfect for integration with n8n AI workflows.

## Quick Start

### For n8n Users
```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/audio:/app/audio",
        "ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0",
        "python", "-m", "mcp_speech_to_text.server"
      ]
    }
  }
}
```

### For Docker Users
```bash
# Pull and run
docker pull ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0
docker run --rm -i -v $(pwd)/audio:/app/audio \
  ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0 \
  python -m mcp_speech_to_text.server
```

## Features

- 🧠 **AI-Powered**: OpenAI Whisper for state-of-the-art transcription
- 🌍 **Multi-Language**: 99+ languages with automatic detection  
- 📁 **Format Support**: 7 audio formats (.wav, .mp3, .m4a, .ogg, .flac, .aac, .wma)
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- 🔗 **MCP Protocol**: Native n8n integration
- ⚡ **Fast**: Optimized for production use

## Available MCP Tools

### 1. `get_supported_formats`
Lists all supported audio formats

### 2. `transcribe_audio` 
Transcribe audio files to text using OpenAI Whisper
```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "file_path": "/app/audio/recording.wav",
    "language": "auto"
  }
}
```

### 3. `convert_audio_format`
Convert audio between different formats

### 4. `record_and_transcribe`
Record audio and transcribe (requires audio device)

## Installation

### Method 1: Docker (Recommended)
```bash
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text
./scripts/build.sh
```

### Method 2: Local Development
```bash
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text
pip install uv
uv pip install -e .
python -m mcp_speech_to_text.server
```

### Method 3: Cross-Platform Scripts

**Windows PowerShell:**
```powershell
.\scripts\build.ps1
.\scripts\start.ps1
```

**Windows CMD:**
```cmd
scripts\build.bat
scripts\start.bat
```

**Linux/macOS:**
```bash
./scripts/build.sh
./scripts/start.sh
```

## n8n Integration

Add to your n8n MCP configuration:
```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/your/audio:/app/audio",
        "ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0",
        "python", "-m", "mcp_speech_to_text.server"
      ],
      "env": {
        "WHISPER_MODEL_SIZE": "base",
        "DEFAULT_LANGUAGE": "auto"
      }
    }
  }
}
```

### Example n8n Workflow
```javascript
// n8n Function Node
const result = await $mcp.tools.call('speech-to-text', 'transcribe_audio', {
  file_path: '/app/audio/meeting-recording.wav',
  language: 'auto'
});

return [{
  json: {
    transcription: result.transcription,
    language: result.language,
    confidence: result.confidence
  }
}];
```

## Testing

```bash
# Basic functionality test
python test_functionality.py

# Comprehensive test
python comprehensive_test.py

# Docker test
docker run --rm mcp-speech-to-text:v1.0.0 python comprehensive_test.py
```

## Future Updates

### Python Version Updates
```bash
# Update Dockerfile: FROM python:3.12-slim
./scripts/build.sh
```

### Package Updates
```bash
# Edit pyproject.toml dependencies
uv pip install -e . --upgrade
```

### Whisper Model Updates
```bash
export WHISPER_MODEL_SIZE=large
docker run -e WHISPER_MODEL_SIZE=large mcp-speech-to-text:v1.0.0
```

## Project Structure

```
mcp-speech-to-text/
├── src/mcp_speech_to_text/
│   └── server.py              # Main MCP server
├── scripts/                   # Cross-platform build scripts
├── tests/                     # Unit tests
├── Dockerfile                 # Docker configuration
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **v1.0.0** - Initial stable release
- **v1.x.x** - Feature additions, bug fixes
- **v2.x.x** - Breaking changes

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/michaelyuwh/mcp-speech-to-text#readme)
- 🐛 [Issues](https://github.com/michaelyuwh/mcp-speech-to-text/issues)
- 💬 [Discussions](https://github.com/michaelyuwh/mcp-speech-to-text/discussions)

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - For the amazing speech recognition model
- [Model Context Protocol](https://modelcontextprotocol.io/) - For the MCP specification
- [n8n](https://n8n.io/) - For the workflow automation platform

---

Made with ❤️ for the AI automation community
