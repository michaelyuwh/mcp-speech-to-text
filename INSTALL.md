# Cross-Platform Installation Guide

This guide provides platform-specific instructions for setting up the MCP Speech-to-Text server on Windows, macOS, and Linux.

## System Requirements

- **Python 3.8 or higher**
- **Git** (for cloning the repository)
- **Docker Desktop** (optional, for containerized deployment)
- **Microphone access** (for recording functionality)

## Platform-Specific Installation

### 🪟 Windows

#### Prerequisites
1. **Install Python**:
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Install Git**:
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Or use GitHub Desktop

3. **Install Docker Desktop** (optional):
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)

#### Installation Options

**Option 1: Command Prompt**
```cmd
REM Clone the repository
git clone <repository-url>
cd mcp-speech-to-text

REM Install uv
pip install uv

REM Run the setup
start.bat
```

**Option 2: PowerShell**
```powershell
# Clone the repository
git clone <repository-url>
Set-Location mcp-speech-to-text

# Install uv
pip install uv

# Run the setup
.\start.ps1
```

**Option 3: Docker**
```cmd
REM Build and run with Docker
build.bat
docker-compose up -d
```

#### Windows-Specific Notes
- **Execution Policy**: If using PowerShell, you may need to run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Microphone Permissions**: Windows may prompt for microphone access
- **Antivirus**: Some antivirus software may flag Python executables

### 🍎 macOS

#### Prerequisites
1. **Install Python**:
   ```bash
   # Using Homebrew (recommended)
   brew install python
   
   # Or download from python.org
   ```

2. **Install Git** (usually pre-installed):
   ```bash
   git --version
   ```

3. **Install Docker Desktop** (optional):
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)

#### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp-speech-to-text

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the setup
./start.sh
```

#### Docker Option
```bash
# Build and run with Docker
./build.sh
docker-compose up -d
```

#### macOS-Specific Notes
- **Microphone Permissions**: macOS will prompt for microphone access
- **Gatekeeper**: May need to allow Python executables in Security & Privacy settings
- **Xcode Command Line Tools**: May be required for some dependencies

### 🐧 Linux

#### Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip git

# Arch Linux
sudo pacman -S python python-pip git
```

#### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp-speech-to-text

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the setup
./start.sh
```

#### Docker Option
```bash
# Install Docker (Ubuntu example)
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER

# Build and run
./build.sh
docker-compose up -d
```

#### Linux-Specific Notes
- **Audio Permissions**: May need to add user to `audio` group
- **PulseAudio/ALSA**: Required for microphone access
- **Firewall**: May need to open port 8000

## Common Installation Issues

### Python Not Found
**Windows:**
```cmd
REM Reinstall Python with PATH option checked
REM Or manually add to PATH: C:\Users\<username>\AppData\Local\Programs\Python\Python3x\
```

**macOS/Linux:**
```bash
# Check if python3 is available instead
python3 --version

# Create alias (add to ~/.bashrc or ~/.zshrc)
alias python=python3
```

### Permission Errors
**Windows:**
```cmd
REM Run Command Prompt as Administrator
REM Or use --user flag: pip install --user uv
```

**macOS/Linux:**
```bash
# Use --user flag
pip install --user uv

# Or fix permissions
sudo chown -R $USER ~/.local
```

### Microphone Access
**Windows:**
- Go to Settings > Privacy & Security > Microphone
- Enable microphone access for Python/Terminal

**macOS:**
- Go to System Preferences > Security & Privacy > Privacy > Microphone
- Allow Terminal/Python to access microphone

**Linux:**
```bash
# Check audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav && aplay test.wav
```

### Docker Issues
**All Platforms:**
```bash
# Check Docker status
docker --version
docker info

# Common fixes
docker system prune
sudo systemctl restart docker  # Linux
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred settings
WHISPER_MODEL_SIZE=base
DEFAULT_LANGUAGE=auto
LOG_LEVEL=INFO
```

## Verification

After installation, verify the setup:

```bash
# Test the server
python -m mcp_speech_to_text.server --help

# Run tests
pytest tests/

# Check Docker image (if using Docker)
docker images mcp-speech-to-text
```

## Getting Help

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Verify prerequisites** are properly installed
3. **Check firewall/antivirus** settings
4. **Review platform-specific notes** above
5. **Open an issue** with your system details and error logs

## Next Steps

Once installed, see:
- [README.md](README.md) for usage instructions
- [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- [examples/](examples/) for integration examples
