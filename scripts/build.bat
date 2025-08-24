@echo off
REM Build script for MCP Speech-to-Text Docker image (Windows)
REM Compatible with Windows Command Prompt and PowerShell

setlocal enabledelayedexpansion

echo Building MCP Speech-to-Text Docker image...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

REM Get version from pyproject.toml (fallback to default)
set VERSION=1.0.0
if exist pyproject.toml (
    for /f "tokens=3 delims= " %%i in ('findstr "^version = " pyproject.toml') do (
        set VERSION=%%i
        set VERSION=!VERSION:"=!
    )
)

echo 📦 Building Docker image: mcp-speech-to-text:!VERSION!
echo.

REM Build the Docker image
docker build -t mcp-speech-to-text:!VERSION! .

if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Build successful
docker tag mcp-speech-to-text:!VERSION! mcp-speech-to-text:latest
echo 🏷️  Tagged as latest

echo.
echo Docker image built successfully:
echo   - mcp-speech-to-text:!VERSION!
echo   - mcp-speech-to-text:latest

REM Display image size
for /f "tokens=*" %%i in ('docker images mcp-speech-to-text:!VERSION! --format "{{.Size}}"') do set IMAGE_SIZE=%%i
echo 📊 Image size: !IMAGE_SIZE!

REM Optional: Push to registry (uncomment if needed)
REM echo Pushing to registry...
REM docker push mcp-speech-to-text:!VERSION!
REM docker push mcp-speech-to-text:latest

echo.
echo 🎉 Build completed!
echo.
echo To run the container:
echo   docker run -p 8000:8000 mcp-speech-to-text:!VERSION!
echo.
echo To run with Docker Compose:
echo   docker-compose up -d
echo.
echo Or use the start.bat script for local development
echo.

pause
