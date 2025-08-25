# Local Offline Speech-to-Text Setup 🎙️

**Completely Local | No Internet Required | No API Costs | Works in Any Region**

This guide sets up speech-to-text functionality that runs completely on your local machine using Vosk models. Perfect for Hong Kong and any region where you want full privacy and no ongoing costs.

## 🚀 Quick Start (60 seconds)

### Option 1: Using uv (Recommended)
```bash
# Clone and setup
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text

# Install with uv (installs Vosk automatically)
uv sync

# Download a basic English model
uv run python -c "
import os, urllib.request, zipfile
os.makedirs('src/mcp_speech_to_text/models', exist_ok=True)
urllib.request.urlretrieve(
    'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
    'model.zip'
)
with zipfile.ZipFile('model.zip') as z:
    z.extractall('src/mcp_speech_to_text/models')
os.remove('model.zip')
print('Model downloaded successfully!')
"

# Run the server
uv run mcp-speech-to-text-offline
```

### Option 2: Using pip
```bash
# Install dependencies
pip install vosk pyaudio pydub mcp

# Clone repository
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text

# Install project
pip install -e .

# Download model (see model section below)
```

### Option 3: Docker (Includes model automatically)
```bash
# Build and run
docker build -t mcp-speech-offline .
docker run -it mcp-speech-offline
```

## 📦 Available Vosk Models

### English Models
```bash
# Small model (39MB) - Fast, good for simple speech
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Standard model (1.8GB) - Better accuracy
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
```

### Chinese Models (Perfect for Hong Kong)
```bash
# Chinese model (1.8GB) - Supports Mandarin and Cantonese
wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip
```

### Other Languages
```bash
# French
wget https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip

# German  
wget https://alphacephei.com/vosk/models/vosk-model-de-0.22.zip

# Spanish
wget https://alphacephei.com/vosk/models/vosk-model-es-0.22.zip

# Russian
wget https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip

# Japanese
wget https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
```

### Install Any Model
```bash
# Download and extract to models directory
cd mcp-speech-to-text
mkdir -p src/mcp_speech_to_text/models
cd src/mcp_speech_to_text/models

# Download your chosen model
wget [MODEL_URL]
unzip *.zip
rm *.zip

# The server will auto-detect the model
```

## 🛠️ Available Tools

### 1. Transcribe Audio Files
```python
# Supports: WAV, MP3, FLAC, M4A, OGG, WEBM, AMR
{
  "tool": "transcribe_audio_offline",
  "arguments": {
    "file_path": "/path/to/audio.mp3",
    "model_language": "en"
  }
}
```

### 2. Convert Audio Formats
```python
# Convert any audio to Vosk-compatible WAV
{
  "tool": "convert_audio_format", 
  "arguments": {
    "input_path": "/path/to/input.mp3",
    "output_path": "/path/to/output.wav",
    "sample_rate": 16000
  }
}
```

### 3. Record and Transcribe
```python
# Record from microphone and transcribe live
{
  "tool": "record_and_transcribe_offline",
  "arguments": {
    "duration": 10,
    "output_file": "recording.wav"  # optional
  }
}
```

### 4. Download Models
```python
# Download models programmatically
{
  "tool": "download_vosk_model",
  "arguments": {
    "language": "en-us",
    "model_size": "small"
  }
}
```

## 🎯 Integration with n8n

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "speech-to-text-offline": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-speech-to-text",
        "run",
        "mcp-speech-to-text-offline"
      ]
    }
  }
}
```

### n8n HTTP Request Node
```javascript
// Convert audio in n8n workflow
{
  "method": "POST",
  "url": "http://localhost:8000/transcribe",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "audio_path": "{{$node['Upload Audio'].binary.data.file_path}}",
    "language": "en"
  }
}
```

## 🔧 Troubleshooting

### PyAudio Installation Issues

**macOS:**
```bash
# Install portaudio first
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

**Windows:**
```powershell
# Use conda (easier)
conda install pyaudio
# Or download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### Audio Format Issues
```bash
# Convert problematic audio files
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav

# Or use the built-in conversion tool
python -c "
from mcp_speech_to_text.server_offline import LocalOfflineSpeechServer
import asyncio
server = LocalOfflineSpeechServer()
result = asyncio.run(server._convert_audio_format({
    'input_path': 'input.mp3',
    'output_path': 'output.wav', 
    'sample_rate': 16000
}))
print(result)
"
```

### Model Not Loading
```bash
# Check models directory
ls -la src/mcp_speech_to_text/models/

# Should contain folders like:
# vosk-model-en-us-0.22/
# vosk-model-cn-0.22/

# If empty, download a model:
cd src/mcp_speech_to_text/models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## ⚡ Performance Optimization

### Model Size vs Performance
| Model Size | File Size | Speed | Accuracy | Use Case |
|------------|-----------|--------|----------|----------|
| Small | 39MB | Very Fast | Good | Quick transcription |
| Medium | 1.8GB | Fast | Excellent | General use |
| Large | 3.4GB | Slower | Best | Critical accuracy |

### Hardware Requirements
- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB RAM, 2 CPU cores  
- **Optimal**: 8GB RAM, 4 CPU cores

### Speed Optimizations
```bash
# Use smaller models for speed
export VOSK_MODEL_SIZE=small

# Process shorter audio chunks
export AUDIO_CHUNK_SIZE=4000

# Use faster audio processing
export AUDIO_SAMPLE_RATE=8000  # Lower quality but faster
```

## 🌟 Advantages of Local Solution

✅ **No Internet Required** - Works completely offline  
✅ **No API Costs** - One-time setup, unlimited usage  
✅ **Privacy** - Audio never leaves your machine  
✅ **Any Region** - Works in Hong Kong, China, anywhere  
✅ **Multi-Language** - 20+ language models available  
✅ **Real-time** - Live transcription from microphone  
✅ **Custom Models** - Train your own models if needed  

## 🔄 Migration from Whisper

If you were using OpenAI Whisper before:

```python
# Old Whisper code
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.wav")
print(result["text"])

# New Vosk equivalent  
import vosk, json, wave
model = vosk.Model("vosk-model-en-us-0.22")
rec = vosk.KaldiRecognizer(model, 16000)
with wave.open("audio.wav", "rb") as wf:
    while True:
        data = wf.readframes(4000)
        if len(data) == 0: break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print(result.get('text', ''))
```

## 📞 Support

- **Documentation**: All guides in this repository
- **Model Issues**: Visit [Vosk Models](https://alphacephei.com/vosk/models/)
- **Audio Issues**: Check troubleshooting section above
- **Performance**: Try different model sizes

This solution gives you complete speech-to-text capabilities without any external dependencies, perfect for Hong Kong and privacy-conscious users!
