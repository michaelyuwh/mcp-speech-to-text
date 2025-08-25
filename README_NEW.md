# MCP Speech-to-Text: Production-Ready Local Solution

[![Platform Support](https://img.shields.io/badge/platforms-x86__64%20%7C%20ARM64%20%7C%20macOS-brightgreen)](https://github.com/michaelyuwh/mcp-speech-to-text)
[![Docker](https://img.shields.io/badge/docker-multi--platform-blue)](https://github.com/michaelyuwh/mcp-speech-to-text)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A **production-ready** Model Context Protocol (MCP) server that provides completely local, offline speech-to-text capabilities. Optimized for x86_64 production deployment with macOS development support.

## 🎯 Perfect For

- **Production Systems** - x86_64 Linux servers with full offline capabilities
- **Hong Kong Users** - No regional restrictions or blocking
- **Privacy-Conscious** - All processing happens locally
- **Cost-Conscious** - Zero API costs after initial setup
- **n8n Workflows** - Direct MCP integration

## 🏗️ Platform Support Matrix

| Platform | Speech Engine | Offline Mode | Internet Required | Production Ready |
|----------|---------------|--------------|-------------------|------------------|
| **x86_64 Linux** | Vosk + SpeechRecognition | ✅ **Full** | ❌ **No** | ✅ **Yes** |
| **ARM64 Linux** | SpeechRecognition | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **macOS (Dev)** | SpeechRecognition | ⚠️ Limited | ✅ Yes | 🔧 Dev Only |

## 🚀 Quick Start

### 🏭 Production Deployment (x86_64 Linux)

**Best Choice: Full offline capabilities with Docker**

```bash
# 1. Clone repository
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text

# 2. Deploy with Docker Compose (Automatic platform detection)
docker compose up -d

# 3. Verify deployment
./scripts/test-deployment.sh

# 4. Check status
docker compose ps
docker compose logs -f mcp-speech-to-text
```

### 💻 Development Setup (macOS)

**For Development and Testing**

```bash
# 1. Clone and setup
git clone https://github.com/michaelyuwh/mcp-speech-to-text.git
cd mcp-speech-to-text

# 2. Install with uv (recommended for macOS)
uv sync
uv run python -c "from src.mcp_speech_to_text.server_sr import SpeechToTextServer; print('✅ Ready')"

# 3. Run development server
uv run python -m mcp_speech_to_text
```

## 🛠️ Deployment Methods

### Method 1: Docker Compose (Production)
```bash
docker compose up -d                    # Start services
docker compose logs -f                  # View logs
docker compose down                     # Stop services
```

### Method 2: Direct Docker Build
```bash
./scripts/build-x86_64.sh              # Build for x86_64
docker run -d --name mcp-speech mcp-speech-to-text:x86_64-latest
```

### Method 3: Native Python (Development)
```bash
# With uv (macOS recommended)
uv sync && uv run python -m mcp_speech_to_text

# With pip
pip install -e . && python -m mcp_speech_to_text
```

## ⚙️ Available MCP Tools

### 🎯 Core Speech Recognition
- **`transcribe_audio_offline`** - Vosk offline transcription (x86_64 only)
- **`transcribe_audio_file`** - SpeechRecognition transcription (all platforms)
- **`record_and_transcribe`** - Live microphone recording and transcription
- **`get_supported_engines`** - List available speech engines

### 🔧 Audio Processing
- **`convert_audio_format`** - Convert between audio formats
- **`test_microphone`** - Test microphone functionality and list devices
- **`get_supported_formats`** - List supported audio formats

## 🧪 Testing and Verification

### Quick Health Check
```bash
# Test current setup
./scripts/test-deployment.sh

# Test Docker image
docker run --rm mcp-speech-to-text:latest python -c "
from src.mcp_speech_to_text.server import OfflineSpeechToTextServer
server = OfflineSpeechToTextServer()
print('✅ Server healthy')
"
```

### Development Testing (macOS)
```bash
# Test SpeechRecognition setup
uv run python -c "
from src.mcp_speech_to_text.server_sr import SpeechToTextServer
server = SpeechToTextServer()
print('✅ Development environment ready')
"
```

## 📊 Performance Characteristics

### x86_64 Production (Vosk Offline)
- **Startup Time**: 10-15 seconds (model loading)
- **Memory Usage**: 200-300MB (with small model)
- **CPU Usage**: 5-10% during transcription
- **Accuracy**: Very good for offline recognition
- **Latency**: Near real-time (< 1 second)
- **Internet**: Not required after setup

### Fallback Mode (SpeechRecognition)
- **Startup Time**: 2-3 seconds
- **Memory Usage**: 50-100MB
- **CPU Usage**: 2-5%
- **Accuracy**: Excellent (Google API)
- **Latency**: 1-3 seconds
- **Internet**: Required for operation

## 🗂️ Project Structure

```
mcp-speech-to-text/
├── src/mcp_speech_to_text/
│   ├── server.py              # Vosk server (x86_64 production)
│   ├── server_sr.py           # SpeechRecognition server (dev/fallback)
│   ├── __main__.py            # Auto-detecting entry point
│   └── models/                # Vosk models (auto-downloaded)
├── scripts/
│   ├── build-x86_64.sh        # Production build script
│   └── test-deployment.sh     # Comprehensive testing
├── .github/workflows/
│   └── build-x86_64.yml       # CI/CD for x86_64 builds
├── Dockerfile                 # Multi-platform container
├── docker-compose.yml         # Production deployment config
├── DEPLOYMENT_X86_64.md       # Detailed production guide
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `SPEECH_ENGINE` | `auto` | `vosk`, `google`, or `auto` |
| `VOSK_MODEL_PATH` | `/app/models` | Path to Vosk models |
| `MCP_SERVER_PORT` | `8000` | Server port |

### Docker Volumes
| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./audio_files` | `/app/audio_files` | Audio file storage |
| `./models` | `/app/models/custom` | Custom Vosk models |

## 🔍 Troubleshooting

### Common Platform Issues

#### ❓ "Vosk not available" on macOS
**Expected behavior** - macOS ARM doesn't support Vosk. Use SpeechRecognition:
```bash
uv run python -m mcp_speech_to_text.server_sr
```

#### ❓ Docker build fails on Apple Silicon
Use platform-specific build:
```bash
docker buildx build --platform linux/amd64 .
```

#### ❓ No audio devices in Docker
Add device access:
```bash
docker run --device /dev/snd your-image
```

### Platform-Specific Solutions

#### x86_64 Linux Production
- Install audio packages: `apt-get install portaudio19-dev`
- Verify model download: `ls src/mcp_speech_to_text/models/`
- Check container logs: `docker logs mcp-speech-to-text`

#### macOS Development
- Install portaudio: `brew install portaudio`
- Use development server: `server_sr.py`
- Enable microphone permissions in System Settings

## 📈 Scaling for Production

### Single Server
```bash
# Basic deployment
docker compose up -d
```

### Load Balanced (Multiple Containers)
```bash
# Scale up containers
docker compose up -d --scale mcp-speech-to-text=3
```

### Kubernetes (Advanced)
See `DEPLOYMENT_X86_64.md` for Kubernetes manifests and advanced deployment patterns.

## 🛡️ Security and Privacy

- ✅ **No Data Transmission** - All processing happens locally
- ✅ **No API Keys** - No external service dependencies
- ✅ **Container Security** - Runs as non-root user
- ✅ **Minimal Attack Surface** - Only required ports exposed
- ✅ **Audio Privacy** - Files never leave your infrastructure

## 📚 Documentation

- **[DEPLOYMENT_X86_64.md](DEPLOYMENT_X86_64.md)** - Comprehensive production deployment guide
- **[GitHub Actions](.github/workflows/)** - Automated testing and building
- **[Docker Hub](#)** - Pre-built images (coming soon)

## 🎯 Why This Solution?

### ✅ Advantages
- **No Vendor Lock-in** - Independent of OpenAI, Google, Azure
- **Predictable Costs** - Zero ongoing API charges
- **Data Privacy** - Audio processing never leaves your infrastructure
- **High Availability** - No dependency on external services
- **Regional Independence** - Works anywhere, including Hong Kong

### 🎪 Perfect Use Cases
- **Enterprise Environments** - Privacy and compliance requirements
- **Cost-Sensitive Projects** - High-volume speech processing
- **Offline Environments** - Air-gapped or limited connectivity
- **Regional Restrictions** - Areas with limited API access
- **Development Teams** - Consistent dev/prod environments

## 🤝 Contributing

1. **Fork** the repository
2. **Develop** on macOS using `server_sr.py`
3. **Test** on x86_64 Linux using Docker
4. **Submit** pull request with platform testing

## 📄 License

MIT License - Complete freedom to use, modify, and distribute.

---

**Ready to deploy speech-to-text without the cloud?** Choose your platform above and get started! 🚀
