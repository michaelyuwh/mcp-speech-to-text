# Multi-platform Docker build optimized for x86_64
FROM --platform=$TARGETPLATFORM python:3.11-slim

# Set build arguments for platform detection
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies for speech recognition
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential \
    wget \
    unzip \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./

# Install uv for better dependency management
RUN pip install --no-cache-dir uv

# Platform-specific dependency installation
RUN echo "Building for platform: $TARGETPLATFORM" && \
    if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        echo "Installing full dependencies with Vosk for x86_64"; \
        uv pip install --system -e ".[all]"; \
    elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        echo "Installing with SpeechRecognition fallback for ARM64"; \
        uv pip install --system -e .; \
    else \
        echo "Installing base dependencies for unknown platform"; \
        uv pip install --system -e .; \
    fi

# Download Vosk model for x86_64 platforms where it's supported
RUN mkdir -p src/mcp_speech_to_text/models && \
    if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        echo "Downloading Vosk model for x86_64 platform"; \
        cd src/mcp_speech_to_text/models && \
        wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
        unzip vosk-model-small-en-us-0.15.zip && \
        rm vosk-model-small-en-us-0.15.zip && \
        echo "Vosk model downloaded successfully"; \
    else \
        echo "Skipping Vosk model download for non-x86_64 platform"; \
        echo "Will use SpeechRecognition fallback"; \
    fi

# Create non-root user
RUN groupadd -r speechuser && useradd -r -g speechuser speechuser
RUN chown -R speechuser:speechuser /app
USER speechuser

# Set environment variables
ENV PYTHONPATH=/app/src
ENV VOSK_MODEL_PATH=/app/src/mcp_speech_to_text/models

# Platform-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        python -c "import vosk; print('✅ Vosk available for x86_64')"; \
    else \
        python -c "import speech_recognition; print('✅ SpeechRecognition available')"; \
    fi || exit 1

# Expose port for potential web interface
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "mcp_speech_to_text.server"]

# Labels
LABEL version="1.0.0"
LABEL description="MCP Speech-to-Text Server"
LABEL maintainer="your.email@example.com"
