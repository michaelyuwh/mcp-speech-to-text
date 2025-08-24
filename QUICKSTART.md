# Quick Start Guide 🚀

## 🎯 Get Started in 60 Seconds

### For n8n Users (Recommended)
```bash
# 1. Add to your n8n MCP configuration:
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/your/audio:/app/audio",
        "ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0",
        "python", "-m", "mcp_speech_to_text.server"
      ]
    }
  }
}

# 2. Create an n8n workflow and use the MCP tools!
```

### For Docker Users
```bash
# Pull and test
docker pull ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0

# Test with sample audio
mkdir audio
# Place your audio files in ./audio/
docker run --rm -i -v $(pwd)/audio:/app/audio \
  ghcr.io/michaelyuwh/mcp-speech-to-text:v1.0.0 \
  python -m mcp_speech_to_text.server
```

### For Developers
```bash
# Clone and build
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text

# Windows PowerShell
.\scripts\build.ps1

# Linux/macOS
./scripts/build.sh
```

## 🛠️ Available Tools

1. **`get_supported_formats`** - List supported audio formats
2. **`transcribe_audio`** - Convert speech to text
3. **`convert_audio_format`** - Convert between formats  
4. **`record_and_transcribe`** - Record and transcribe

## 📝 Example Usage

```javascript
// In n8n Function Node
const result = await $mcp.tools.call('speech-to-text', 'transcribe_audio', {
  file_path: '/app/audio/meeting.wav',
  language: 'auto'
});

return [{ json: { transcription: result.transcription } }];
```

## 🆘 Need Help?

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/michaelyuwh/mcp-speech-to-text/issues)
- 💬 [Discussions](https://github.com/michaelyuwh/mcp-speech-to-text/discussions)

**That's it! You're ready to build amazing speech-to-text workflows! 🎉**
