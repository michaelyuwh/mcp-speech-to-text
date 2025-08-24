# 🎯 MCP Speech-to-Text for n8n - READY TO USE!

## ✅ **Setup Complete**
Your MCP Speech-to-Text Docker image is built and ready for n8n integration!

**Image**: `mcp-speech-to-text:1.0.0`

## 🔗 **n8n Integration Guide**

### Method 1: Direct Docker Integration (Recommended)

Add this to your **n8n MCP configuration**:

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/Users/michaelyu/Project/n8n/MCP/speech-to-text/audio:/app/audio",
        "mcp-speech-to-text:1.0.0",
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

### Method 2: Using Docker Compose (Alternative)

Create `docker-compose.yml` for your n8n setup:

```yaml
version: '3.8'
services:
  n8n:
    # your n8n configuration
    
  mcp-speech-to-text:
    image: mcp-speech-to-text:1.0.0
    volumes:
      - ./audio:/app/audio
    environment:
      - WHISPER_MODEL_SIZE=base
      - DEFAULT_LANGUAGE=auto
    stdin_open: true
    tty: true
```

## 🛠️ **Available MCP Tools**

### 1. `get_supported_formats`
Lists all supported audio formats
```javascript
// n8n usage:
const formats = await $mcp.tools.call('speech-to-text', 'get_supported_formats', {});
// Returns: [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".wma"]
```

### 2. `transcribe_audio`
Transcribe audio files to text using OpenAI Whisper
```javascript
// n8n usage:
const result = await $mcp.tools.call('speech-to-text', 'transcribe_audio', {
  file_path: '/app/audio/meeting-recording.wav',
  language: 'auto'  // or 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'
});
```

### 3. `convert_audio_format`
Convert audio between different formats
```javascript
// n8n usage:
const conversion = await $mcp.tools.call('speech-to-text', 'convert_audio_format', {
  input_path: '/app/audio/input.mp3',
  output_path: '/app/audio/output.wav',
  output_format: 'wav'
});
```

### 4. `record_and_transcribe`
Record audio and transcribe (requires audio device - may not work in Docker)
```javascript
// n8n usage:
const recording = await $mcp.tools.call('speech-to-text', 'record_and_transcribe', {
  duration: 10.0,
  language: 'auto'
});
```

## 📁 **File Management for n8n**

### Audio File Location
Place your audio files in the mounted directory:
```bash
# Host directory (automatically mounted to Docker)
/Users/michaelyu/Project/n8n/MCP/speech-to-text/audio/

# Examples:
./audio/meeting.wav
./audio/interview.mp3
./audio/recording.m4a
```

### In MCP Tool Calls
Use these paths in your n8n MCP tool calls:
```javascript
// Container paths for MCP tools
'/app/audio/meeting.wav'
'/app/audio/interview.mp3'
'/app/audio/recording.m4a'
```

## 🎯 **Example n8n Workflow**

### Simple Transcription Workflow:
1. **HTTP Request** - Receive file upload
2. **File Save** - Save to `./audio/` directory  
3. **MCP Tool** - Call `transcribe_audio`
4. **Process Text** - Use transcription in workflow
5. **Response** - Return results

### Advanced Processing Workflow:
```javascript
// n8n Function Node example
const audioFile = $input.first().binary?.data;

// Save file
const fileName = `recording-${Date.now()}.wav`;
await $fs.writeFile(`./audio/${fileName}`, audioFile);

// Transcribe using MCP
const transcription = await $mcp.tools.call('speech-to-text', 'transcribe_audio', {
  file_path: `/app/audio/${fileName}`,
  language: 'auto'
});

// Process result
return [{
  json: {
    originalFile: fileName,
    transcription: transcription.transcription,
    language: transcription.language,
    confidence: transcription.confidence,
    timestamp: new Date().toISOString()
  }
}];
```

## 🧪 **Testing Your Setup**

### 1. Test Docker Image
```bash
# Test if image works
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
docker run --rm -i mcp-speech-to-text:1.0.0 python -m mcp_speech_to_text.server
```

### 2. Test with Sample Audio
```bash
# Create a test audio file (optional)
# Place any .wav, .mp3, or other supported audio file in ./audio/

# Test transcription
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "transcribe_audio", "arguments": {"file_path": "/app/audio/test.wav"}}}' | \
docker run --rm -i -v $(pwd)/audio:/app/audio mcp-speech-to-text:1.0.0 python -m mcp_speech_to_text.server
```

## 🔧 **Troubleshooting**

### Common Issues:
1. **File not found**: Ensure audio files are in the `./audio/` directory
2. **Permission errors**: Check file permissions in the audio directory
3. **Format not supported**: Use one of the 7 supported formats
4. **n8n connection**: Verify MCP server configuration in n8n settings

### Debug Commands:
```bash
# Check if Docker image exists
docker images | grep mcp-speech-to-text

# Test basic functionality
docker run --rm mcp-speech-to-text:1.0.0 python comprehensive_test.py

# Check audio directory
ls -la ./audio/
```

## 🎉 **You're Ready!**

Your MCP Speech-to-Text is now ready for n8n integration:
- ✅ Docker image built and tested
- ✅ All 4 tools available
- ✅ Audio mounting configured  
- ✅ n8n configuration provided
- ✅ Example workflows included

**Start building powerful speech-to-text workflows in n8n!** 🚀

### Next Steps:
1. Add the MCP configuration to your n8n settings
2. Create a test workflow with audio file upload
3. Use the `transcribe_audio` tool to convert speech to text
4. Build amazing AI workflows with voice capabilities!
