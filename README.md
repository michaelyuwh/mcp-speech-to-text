# MCP Speech-to-Text Server

A Model Context Protocol (MCP) server that provides speech-to-text capabilities using OpenAI Whisper for n8n AI workflows.

## Quick Start

### n8n Integration
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

### Docker Usage
```bash
docker pull ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0
docker run --rm -i -v $(pwd)/audio:/app/audio \
  ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0 \
  python -m mcp_speech_to_text.server
```

## Features

- AI-powered transcription using OpenAI Whisper
- Multi-language support (99+ languages)
- 7 audio formats supported (.wav, .mp3, .m4a, .ogg, .flac, .aac, .wma)
- Docker containerized for easy deployment
- Native n8n MCP integration
- Cross-platform support (Windows, macOS, Linux)

## Available MCP Tools

1. **get_supported_formats** - List supported audio formats
2. **transcribe_audio** - Convert audio files to text
3. **convert_audio_format** - Convert between audio formats
4. **record_and_transcribe** - Record and transcribe audio

## Installation

### Build from Source
```bash
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text
./scripts/build.sh
```

### Cross-Platform Scripts
- Windows: `scripts\build.ps1` or `scripts\build.bat`
- Linux/macOS: `./scripts/build.sh`

## Example Usage

```javascript
// n8n Function Node
const result = await $mcp.tools.call('speech-to-text', 'transcribe_audio', {
  file_path: '/app/audio/recording.wav',
  language: 'auto'
});

return [{ json: { transcription: result.transcription } }];
```

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](INSTALL.md)
- [Development Guide](DEVELOPMENT.md)
- [Changelog](CHANGELOG.md)

## Support

- [Issues](https://github.com/michaelyuwh/mcp-speech-to-text/issues)
- [Discussions](https://github.com/michaelyuwh/mcp-speech-to-text/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details.
