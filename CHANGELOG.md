# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0] - 2025-08-25

### Added
- Initial stable release of MCP Speech-to-Text server
- OpenAI Whisper integration for state-of-the-art transcription
- Support for 7 audio formats (.wav, .mp3, .m4a, .ogg, .flac, .aac, .wma)
- Multi-language support with automatic detection
- Docker containerization with full deployment support
- Cross-platform build scripts (Windows PowerShell, CMD, Linux/macOS)
- Comprehensive MCP protocol implementation
- n8n integration support and documentation
- 4 core MCP tools:
  - `get_supported_formats` - List supported audio formats
  - `transcribe_audio` - Transcribe audio files to text
  - `convert_audio_format` - Convert between audio formats
  - `record_and_transcribe` - Real-time recording and transcription
- Robust error handling and logging
- Health checks and monitoring
- Comprehensive test suite
- Production-ready Docker image (2.73GB optimized)
- Complete documentation and examples

### Technical Features
- Python 3.11+ support
- UV package manager integration
- Automatic dependency management
- Graceful handling of optional dependencies
- Environment variable configuration
- Configurable Whisper model sizes
- Memory-efficient operation
- Cross-platform compatibility

### Documentation
- Complete README with installation guides
- n8n integration examples
- Docker deployment instructions
- Cross-platform setup guides
- API documentation for all MCP tools
- Troubleshooting guides
- Contributing guidelines

### Infrastructure
- MIT License
- Semantic versioning
- GitHub Actions ready
- Docker Hub / GHCR compatible
- Production deployment guides

## Future Roadmap

### [v1.1.0] - Planned
- Additional language model support
- Streaming transcription capabilities
- Enhanced audio preprocessing
- Performance optimizations
- Extended format support

### [v1.2.0] - Planned
- Real-time transcription streaming
- Audio quality enhancement
- Batch processing capabilities
- Advanced configuration options

### [v2.0.0] - Future
- Breaking changes for major improvements
- New MCP protocol versions
- Enhanced AI model integration
- Advanced audio processing pipeline
