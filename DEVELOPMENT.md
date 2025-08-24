# MCP Speech-to-Text Development Guide

## Quick Start

### 1. Local Development

#### Linux/macOS:
```bash
# Clone or navigate to the project
cd /Users/michaelyu/Project/n8n/MCP/speech-to-text

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Start the server
./start.sh
```

#### Windows (Command Prompt):
```cmd
REM Navigate to the project
cd C:\path\to\n8n\MCP\speech-to-text

REM Install uv if not already installed
pip install uv

REM Start the server
start.bat
```

#### Windows (PowerShell):
```powershell
# Navigate to the project
Set-Location "C:\path\to\n8n\MCP\speech-to-text"

# Install uv if not already installed
pip install uv

# Start the server
.\start.ps1
```

### 2. Docker Development

#### All Platforms:
```bash
# Build the Docker image
# Linux/macOS: ./build.sh
# Windows: build.bat or .\build.ps1

# Run with Docker Compose
docker-compose up -d

# Or run directly
docker run -p 8000:8000 mcp-speech-to-text:v1.0.0
```

## Development Workflow

### Setting up the Environment

#### Linux/macOS:
1. **Create virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. **Install development dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

#### Windows (Command Prompt):
1. **Create virtual environment:**
   ```cmd
   uv venv
   .venv\Scripts\activate.bat
   ```

2. **Install development dependencies:**
   ```cmd
   uv pip install -e ".[dev]"
   ```

#### Windows (PowerShell):
1. **Create virtual environment:**
   ```powershell
   uv venv
   .venv\Scripts\Activate.ps1
   ```

2. **Install development dependencies:**
   ```powershell
   uv pip install -e ".[dev]"
   ```

#### All Platforms:
3. **Install pre-commit hooks (optional):**
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_speech_to_text

# Run specific test file
pytest tests/test_server.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
speech-to-text/
├── src/
│   └── mcp_speech_to_text/
│       ├── __init__.py
│       └── server.py           # Main MCP server implementation
├── tests/
│   ├── __init__.py
│   └── test_server.py          # Unit tests
├── examples/
│   ├── usage_example.py        # Usage examples
│   └── n8n_workflow_example.json  # n8n workflow template
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── start.sh                    # Startup script
├── build.sh                    # Build script
├── test_server.py              # Integration test
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

## Key Components

### MCP Server (`server.py`)

The main server implements the Model Context Protocol with these tools:

1. **transcribe_audio**: Transcribe audio files using Whisper
2. **record_and_transcribe**: Record from microphone and transcribe
3. **get_supported_formats**: List supported audio formats
4. **convert_audio_format**: Convert between audio formats

### Configuration

Environment variables (see `.env.example`):
- `WHISPER_MODEL_SIZE`: Model size (tiny, base, small, medium, large)
- `DEFAULT_LANGUAGE`: Default language for transcription
- `LOG_LEVEL`: Logging level

### Docker Support

- Multi-stage build for optimized image size
- Health checks for container monitoring
- Non-root user for security
- Volume mounts for audio files

## Integration with n8n

### HTTP Request Configuration

```json
{
  "method": "POST",
  "url": "http://localhost:8000/tools/call",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "transcribe_audio",
    "arguments": {
      "audio_file_path": "/path/to/audio.wav",
      "language": "auto"
    }
  }
}
```

### Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"transcription\": \"Hello world\", \"detected_language\": \"en\", \"model_used\": \"base\"}"
    }
  ],
  "isError": false
}
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure PYTHONPATH is set correctly
2. **Model download fails**: Check internet connection and disk space
3. **Audio format not supported**: Use conversion tool first
4. **Microphone access denied**: Check system permissions

### Debugging

1. **Enable debug logging:**
   ```bash
   export LOG_LEVEL=DEBUG
   ```

2. **Test individual components:**
   ```bash
   python test_server.py
   ```

3. **Check Docker logs:**
   ```bash
   docker-compose logs -f
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Performance Considerations

- **Model Size**: Larger models provide better accuracy but require more resources
- **Audio Format**: WAV files process faster than compressed formats
- **Concurrent Requests**: Server can handle multiple requests but model loading is memory-intensive
- **File Size Limits**: Consider implementing file size limits for production use

## Security Notes

- **File Access**: Server has access to local file system
- **Network Security**: Consider using HTTPS in production
- **Input Validation**: All file paths and parameters are validated
- **Container Security**: Runs as non-root user in Docker
