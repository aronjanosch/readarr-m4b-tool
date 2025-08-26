# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ReadarrM4B is a unified audiobook converter that integrates with Readarr to automatically convert multi-file MP3 audiobooks into single M4B files. It operates in two modes: direct CLI execution and HTTP API server for container deployments.

**External Dependencies Required:**
- Python 3.11+
- ffmpeg (audio processing)
- m4b-tool (audiobook conversion engine)

## Development Commands

**Installation:**
```bash
pip install -r requirements.txt
```

**Configuration Testing:**
```bash
python src/main.py --test
```

**Manual Conversion:**
```bash
python src/main.py --convert "/path/to/Author/Book Title"
```

**HTTP Server Mode:**
```bash
python src/main.py --server
# Custom port:
export WEBHOOK_PORT=8080 && python src/main.py --server
```

**Testing:**
```bash
# Full test suite
python tests/run_tests.py

# Individual test modules
python tests/test_main.py
python tests/test_config.py  
python tests/test_utils.py
```

## Architecture

**Core Modules (`/src/`):**
- `main.py` - Dual-mode entry point (CLI + HTTP server) with `WebhookHandler` and `ReadarrM4BServer`
- `config.py` - YAML-based configuration with dataclass validation (`PathConfig`, `ConversionConfig`, `LoggingConfig`)
- `converter.py` - Core conversion logic in `M4BConverter` class, handles file stability and m4b-tool execution
- `utils.py` - Logging setup, filename sanitization, and directory utilities

**Configuration:**
- Primary config file: `config/config.yaml`
- Supports environment variable expansion in paths
- Dataclass-based validation with sensible defaults

**Integration Patterns:**
- **CLI Mode**: Direct Python execution triggered by Readarr custom scripts
- **HTTP Mode**: Webhook-style API server for container-based deployments
- Uses Readarr environment variables (`readarr_author_name`, `readarr_book_title`) when available

**Key Architecture Decisions:**
- Async/await pattern throughout for non-blocking operations
- File stability checking before processing (configurable wait time)
- Single unified codebase supporting both deployment modes
- Clean separation of concerns across modules
- Comprehensive logging at multiple levels

**Testing Framework:**
- Python unittest with mocking and temporary file handling
- Tests cover configuration loading, environment variable expansion, and command validation
- Use `python tests/run_tests.py` for comprehensive test execution

**Deployment Notes:**
- Container support with Dockerfile and docker-compose.yml
- Shared volume architecture for Readarr integration
- Health checking and graceful error handling
- Optional cleanup of original files after successful conversion