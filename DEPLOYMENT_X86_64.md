# MCP Speech-to-Text: x86_64 Production Deployment Guide

This guide covers deploying the MCP Speech-to-Text server on x86_64 production systems using Docker.

## Quick Start for x86_64 Production

### Option 1: Docker Compose (Recommended)

```bash
# Clone or copy the project to your x86_64 server
git clone <repository-url>
cd mcp-speech-to-text

# Start the service (automatically downloads Vosk model)
docker compose up -d

# Check status
docker compose ps
docker compose logs mcp-speech-to-text
```

### Option 2: Direct Docker Build

```bash
# Build specifically for x86_64
./scripts/build-x86_64.sh

# Run the container
docker run -d \
  --name mcp-speech-to-text \
  --restart unless-stopped \
  -v $(pwd)/audio_files:/app/audio_files \
  -p 8000:8000 \
  mcp-speech-to-text:x86_64-latest
```

### Option 3: Pre-built Image (when available)

```bash
# Pull and run pre-built image
docker pull ghcr.io/michaelyuwh/mcp-speech-to-text:x86_64-latest
docker run -d \
  --name mcp-speech-to-text \
  --restart unless-stopped \
  ghcr.io/michaelyuwh/mcp-speech-to-text:x86_64-latest
```

## Platform Support Matrix

| Platform | Vosk Support | SpeechRecognition | Offline Mode | Production Ready |
|----------|--------------|-------------------|---------------|------------------|
| x86_64   | ✅ Full      | ✅ Full          | ✅ Yes        | ✅ Yes           |
| ARM64    | ❌ Limited   | ✅ Full          | ⚠️ Partial    | ✅ Yes           |
| macOS    | ❌ No        | ✅ Full          | ⚠️ Limited    | ⚠️ Dev only      |

## Features by Platform

### x86_64 (Linux) - Full Featured
- ✅ Vosk offline speech recognition (no internet required)
- ✅ SpeechRecognition library with Google API
- ✅ Complete MCP protocol support
- ✅ Audio format conversion
- ✅ Microphone recording
- ✅ Docker containerization
- ✅ Production deployment ready

### ARM64 (Linux) - Fallback Mode
- ❌ Vosk (not supported on ARM64)
- ✅ SpeechRecognition library
- ✅ Google Speech API (requires internet)
- ✅ MCP protocol support
- ✅ Docker containerization

### macOS (Development)
- ❌ Vosk (limited macOS ARM support)
- ✅ SpeechRecognition library
- ✅ Development and testing
- ❌ Not recommended for production

## Verification Commands

### Test x86_64 Build Locally
```bash
# Test using Docker emulation on macOS
docker buildx build --platform linux/amd64 --load -t test-x86 .
docker run --rm --platform linux/amd64 test-x86 python -c "
import vosk
from src.mcp_speech_to_text.server import OfflineSpeechToTextServer
server = OfflineSpeechToTextServer()
print('✅ x86_64 build working properly')
"
```

### Health Check on Production Server
```bash
# Check container health
docker exec mcp-speech-to-text python -c "
import vosk
import speech_recognition
from src.mcp_speech_to_text.server import OfflineSpeechToTextServer
server = OfflineSpeechToTextServer()
print('✅ Production deployment healthy')
"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `/app/src` | Python module path |
| `VOSK_MODEL_PATH` | `/app/src/mcp_speech_to_text/models` | Vosk model location |
| `SPEECH_ENGINE` | `auto` | Speech engine selection |

## Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./audio_files` | `/app/audio_files` | Audio file storage |
| `./models` | `/app/src/mcp_speech_to_text/models/custom` | Custom models |

## Performance Characteristics

### x86_64 with Vosk
- **Startup time**: ~10-15 seconds (model loading)
- **Memory usage**: ~200-300MB (with small model)
- **CPU usage**: Low (~5-10% during transcription)
- **Accuracy**: Very good for offline recognition
- **Latency**: Near real-time (< 1 second)

### Fallback with SpeechRecognition
- **Startup time**: ~2-3 seconds
- **Memory usage**: ~50-100MB
- **CPU usage**: Low (~2-5%)
- **Accuracy**: Excellent (Google API)
- **Latency**: 1-3 seconds (network dependent)

## Troubleshooting

### Common x86_64 Issues

#### Vosk Model Not Loading
```bash
# Check model exists
docker exec mcp-speech-to-text ls -la /app/src/mcp_speech_to_text/models/

# Re-download model
docker exec mcp-speech-to-text bash -c "
cd /app/src/mcp_speech_to_text/models && \
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
unzip vosk-model-small-en-us-0.15.zip
"
```

#### Audio Device Issues
```bash
# Check audio devices
docker run --rm --device /dev/snd mcp-speech-to-text:x86_64-latest \
  python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"
```

### Build Issues

#### Docker Buildx Not Available
```bash
# Setup buildx
docker buildx create --use
docker buildx inspect --bootstrap
```

#### Platform Mismatch
```bash
# Force platform
docker buildx build --platform linux/amd64 --load .
```

## Production Deployment Checklist

- [ ] x86_64 Linux server
- [ ] Docker and Docker Compose installed
- [ ] Sufficient RAM (1GB+ recommended)
- [ ] Network access for initial model download
- [ ] Audio devices configured (if using microphone)
- [ ] Firewall rules for port 8000 (if using web interface)
- [ ] Monitoring and logging configured
- [ ] Backup strategy for audio files
- [ ] SSL/TLS termination (if exposing to internet)

## Security Considerations

- Container runs as non-root user
- No sensitive data stored in image
- Audio files should be encrypted at rest
- Network traffic should use HTTPS
- Regular security updates recommended

## Monitoring

```bash
# Container stats
docker stats mcp-speech-to-text

# Health check
curl http://localhost:8000/health

# Logs
docker logs -f mcp-speech-to-text
```

## Scaling

For high-load production:
- Use load balancer with multiple containers
- Implement audio file queuing system
- Consider GPU acceleration for larger Vosk models
- Set up horizontal pod autoscaling in Kubernetes

## Support

This deployment configuration is optimized for x86_64 production systems and provides the best performance and offline capabilities available.
