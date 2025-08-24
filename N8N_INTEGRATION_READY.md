# 🚀 MCP Speech-to-Text Server for n8n - RUNNING!

## ✅ **Server Status**
Your MCP Speech-to-Text server is now **running and ready for n8n integration**!

- **Container Name**: `mcp-speech-to-text-n8n`
- **Status**: ✅ Running with stdio interface (proper MCP protocol)
- **Audio Directory**: `./audio` (mounted to `/app/audio` in container)
- **Restart Policy**: `unless-stopped` (automatically restarts)

## 🔗 **n8n Configuration**

### 1. Add to n8n MCP Configuration
Add this to your n8n MCP servers configuration:

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "exec", "-i", 
        "mcp-speech-to-text-n8n", 
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

### 2. Alternative: Direct Docker Command for n8n
```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/your/audio:/app/audio",
        "mcp-speech-to-text:1.0.0",
        "python", "-m", "mcp_speech_to_text.server"
      ]
    }
  }
}
```

## 🛠️ **Available MCP Tools for n8n**

### 1. `get_supported_formats`
```javascript
// Lists all supported audio formats
{
  "tool": "get_supported_formats",
  "arguments": {}
}
// Returns: [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"]
```

### 2. `transcribe_audio`
```javascript
// Transcribe audio file to text
{
  "tool": "transcribe_audio",
  "arguments": {
    "file_path": "/app/audio/recording.wav",
    "language": "auto"  // or "en", "es", "fr", etc.
  }
}
```

### 3. `convert_audio_format`
```javascript
// Convert audio between formats
{
  "tool": "convert_audio_format",
  "arguments": {
    "input_path": "/app/audio/input.mp3",
    "output_path": "/app/audio/output.wav",
    "output_format": "wav"
  }
}
```

### 4. `record_and_transcribe`
```javascript
// Record and transcribe (requires audio device)
{
  "tool": "record_and_transcribe",
  "arguments": {
    "duration": 10.0,
    "language": "auto"
  }
}
```

## 📁 **File Management**

### Upload Audio Files
Place your audio files in the `audio` directory:
```bash
# Local directory (automatically mounted to container)
./audio/my-recording.wav
./audio/interview.mp3
./audio/meeting.m4a
```

### In Container Paths
```bash
# These paths are used in MCP tool calls
/app/audio/my-recording.wav
/app/audio/interview.mp3
/app/audio/meeting.m4a
```

## 🎯 **Testing with n8n**

### Basic Workflow Example:
1. **Upload Node**: Upload audio file to n8n
2. **File Save**: Save to `./audio/` directory
3. **MCP Tool Call**: Use `transcribe_audio` tool
4. **Text Processing**: Process the transcription result

### Sample n8n Node Configuration:
```javascript
// In an n8n Code/Function node
const result = await this.helpers.callMcp('speech-to-text', 'transcribe_audio', {
  file_path: '/app/audio/uploaded-file.wav',
  language: 'auto'
});

return [{
  json: {
    original_file: 'uploaded-file.wav',
    transcription: result.transcription,
    language: result.language,
    confidence: result.confidence
  }
}];
```

## 🔧 **Container Management**

### Check Status
```bash
docker ps | grep mcp-speech-to-text-n8n
```

### View Logs
```bash
docker logs mcp-speech-to-text-n8n
```

### Stop/Start
```bash
docker stop mcp-speech-to-text-n8n
docker start mcp-speech-to-text-n8n
```

### Restart
```bash
docker restart mcp-speech-to-text-n8n
```

## 🎉 **Ready for Production!**

Your MCP Speech-to-Text server is now:
- ✅ Running in Docker with proper MCP protocol
- ✅ Configured for n8n integration
- ✅ Audio file mounting ready
- ✅ Auto-restart enabled
- ✅ All 4 tools available and tested

**Start building your n8n AI workflows with speech-to-text capabilities!** 🚀
