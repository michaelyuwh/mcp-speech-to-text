FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./
COPY test_functionality.py ./
COPY test_tools.py ./
COPY comprehensive_test.py ./
COPY http_server.py ./
COPY docker-entrypoint.sh ./

# Install dependencies using uv
RUN uv pip install --system -e .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Create non-root user
RUN useradd -m -u 1001 mcp
USER mcp

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV WHISPER_MODEL_SIZE=base
ENV DEFAULT_LANGUAGE=auto

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the MCP server
CMD ["./docker-entrypoint.sh"]

# Labels
LABEL version="1.0.0"
LABEL description="MCP Speech-to-Text Server"
LABEL maintainer="your.email@example.com"
