@echo off
REM MCP Speech-to-Text Server Startup Script (Windows)
REM Compatible with Windows Command Prompt and PowerShell

setlocal enabledelayedexpansion

echo 🎤 MCP Speech-to-Text Server v1.0.0
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ uv is not installed. Installing uv...
    echo Please install uv manually from: https://github.com/astral-sh/uv
    echo Or use: pip install uv
    pause
    exit /b 1
)

REM Set default environment variables if not already set
if not defined WHISPER_MODEL_SIZE set WHISPER_MODEL_SIZE=base
if not defined DEFAULT_LANGUAGE set DEFAULT_LANGUAGE=auto
if not defined LOG_LEVEL set LOG_LEVEL=INFO

echo 📋 Configuration:
echo   Whisper Model: %WHISPER_MODEL_SIZE%
echo   Default Language: %DEFAULT_LANGUAGE%
echo   Log Level: %LOG_LEVEL%
echo.

REM Check if running in Docker (Windows containers)
if exist "C:\ProgramData\docker" (
    if defined DOCKER_CONTAINER (
        echo 🐳 Running in Docker container
        set PYTHONPATH=C:\app\src
        cd C:\app
        goto :start_server
    )
)

echo 💻 Running locally on Windows
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    uv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo 📦 Installing dependencies...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment activation script not found
    pause
    exit /b 1
)

uv pip install -e .
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Set PYTHONPATH for Windows
set PYTHONPATH=%CD%\src

:start_server
REM Download Whisper model if needed
echo 🤖 Checking Whisper model...
python -c "import whisper; whisper.load_model('%WHISPER_MODEL_SIZE%')" >nul 2>&1
if errorlevel 1 (
    echo 📥 Downloading Whisper model (%WHISPER_MODEL_SIZE%)...
    python -c "import whisper; whisper.load_model('%WHISPER_MODEL_SIZE%')"
    if errorlevel 1 (
        echo ❌ Failed to download Whisper model
        pause
        exit /b 1
    )
)

echo ✅ Setup complete!
echo 🚀 Starting MCP Speech-to-Text server...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m mcp_speech_to_text.server

pause
