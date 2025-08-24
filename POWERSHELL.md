# PowerShell Quick Reference for MCP Speech-to-Text

This guide provides PowerShell-specific commands and tips for working with the MCP Speech-to-Text server.

## 🚀 Quick Start Commands

### Basic Usage
```powershell
# Start the server (recommended)
.\start.ps1

# Start with development mode
.\start.ps1 -Dev -Verbose

# Build Docker image
.\build.ps1

# Development helper
.\dev.ps1 help
```

### Advanced Usage
```powershell
# Start with custom configuration
.\start.ps1 -WhisperModelSize "small" -DefaultLanguage "en" -LogLevel "DEBUG"

# Skip model download (if already cached)
.\start.ps1 -SkipModelDownload

# Build and push to registry
.\build.ps1 -Push -Registry "myregistry.com" -Verbose

# No pause mode (for automation)
.\start.ps1 -NoPause
.\build.ps1 -NoPause
```

## 🛠️ Development Workflow

### Development Helper Script
```powershell
# Show all available commands
.\dev.ps1 help

# Setup development environment
.\dev.ps1 install

# Start development server
.\dev.ps1 start

# Run tests
.\dev.ps1 test

# Code quality
.\dev.ps1 lint
.\dev.ps1 format

# Build Docker image
.\dev.ps1 build

# Clean up artifacts
.\dev.ps1 clean

# Show project status
.\dev.ps1 status
```

### Manual Development Setup
```powershell
# Create and activate virtual environment
uv venv
.\.venv\Scripts\Activate.ps1

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests manually
python -m pytest tests/ -v
python test_server.py

# Code formatting
python -m black src/ tests/
python -m ruff check --fix src/ tests/

# Type checking
python -m mypy src/
```

## 🔧 Configuration & Environment

### Setting Environment Variables
```powershell
# Temporary (current session)
$env:WHISPER_MODEL_SIZE = "base"
$env:DEFAULT_LANGUAGE = "auto"
$env:LOG_LEVEL = "INFO"

# Persistent (current user)
[Environment]::SetEnvironmentVariable("WHISPER_MODEL_SIZE", "base", "User")
[Environment]::SetEnvironmentVariable("DEFAULT_LANGUAGE", "auto", "User")
[Environment]::SetEnvironmentVariable("LOG_LEVEL", "INFO", "User")

# Using .env file (recommended)
Copy-Item .env.example .env
# Edit .env file with your preferred settings
```

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for specific script
PowerShell -ExecutionPolicy Bypass -File .\start.ps1
```

## 🐳 Docker Commands

### Basic Docker Operations
```powershell
# Build image
.\build.ps1

# Build with verbose output
.\build.ps1 -Verbose

# Build and push to registry
.\build.ps1 -Push -Registry "your-registry.com"

# Run container
docker run -p 8000:8000 mcp-speech-to-text:v1.0.0

# Run with Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Docker Management
```powershell
# List images
docker images mcp-speech-to-text

# Remove old images
docker rmi mcp-speech-to-text:old-version

# Clean up Docker system
docker system prune -f

# View container logs
docker logs container-name
```

## 🧪 Testing & Debugging

### Running Tests
```powershell
# All tests with development helper
.\dev.ps1 test

# Manual test execution
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v --tb=short
python test_server.py

# Test with coverage
python -m pytest tests/ --cov=mcp_speech_to_text --cov-report=html
```

### Debugging
```powershell
# Start with debug logging
.\start.ps1 -LogLevel "DEBUG" -Verbose

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify installation
python -c "import mcp_speech_to_text; print('Import successful')"

# Test Whisper model
python -c "import whisper; model = whisper.load_model('base'); print('Model loaded')"

# Check port availability
netstat -an | Select-String ":8000"
```

## 📊 Monitoring & Status

### Project Status
```powershell
# Development helper status
.\dev.ps1 status

# Manual checks
python --version
uv --version
docker --version

# Check virtual environment
Test-Path .venv
.\.venv\Scripts\Activate.ps1; uv pip list

# Check installed packages
python -m pip list | Select-String -Pattern "whisper|mcp|speech"
```

### Performance Monitoring
```powershell
# CPU and memory usage
Get-Process python | Format-Table Name, CPU, WorkingSet

# Docker container stats
docker stats --no-stream

# Check disk space for models
Get-ChildItem $env:USERPROFILE\.cache\whisper -Recurse | Measure-Object -Property Length -Sum
```

## 🔍 Troubleshooting

### Common Issues and Solutions

**Import Errors:**
```powershell
# Check PYTHONPATH
echo $env:PYTHONPATH

# Set PYTHONPATH manually
$env:PYTHONPATH = "$PWD\src"
```

**Virtual Environment Issues:**
```powershell
# Recreate virtual environment
Remove-Item .venv -Recurse -Force
.\dev.ps1 install
```

**Permission Errors:**
```powershell
# Run as administrator if needed
Start-Process PowerShell -Verb RunAs

# Or change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Docker Issues:**
```powershell
# Restart Docker Desktop
Restart-Service docker
# or restart Docker Desktop application

# Clear Docker cache
docker builder prune -f
docker system prune -f
```

**Model Download Issues:**
```powershell
# Clear model cache
Remove-Item $env:USERPROFILE\.cache\whisper -Recurse -Force

# Download manually
python -c "import whisper; whisper.load_model('base')"
```

## 📚 Additional Resources

### PowerShell Profile Setup
Add to your PowerShell profile for convenience:
```powershell
# Edit profile
notepad $PROFILE

# Add aliases
function mcp-start { .\start.ps1 @args }
function mcp-build { .\build.ps1 @args }
function mcp-dev { .\dev.ps1 @args }
```

### VS Code Integration
```powershell
# Open project in VS Code
code .

# Run tasks in VS Code
Ctrl+Shift+P -> "Tasks: Run Task"
```

### Useful PowerShell Modules
```powershell
# Install useful modules
Install-Module -Name PSReadLine -Force
Install-Module -Name Terminal-Icons -Force
Install-Module -Name posh-git -Force
```

For more detailed information, see the main [README.md](README.md) and [DEVELOPMENT.md](DEVELOPMENT.md) files.
