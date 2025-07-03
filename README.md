# ReadarrM4B

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Unified audiobook converter for Readarr**

Seamlessly converts MP3 audiobooks to M4B format with proper chapters when Readarr downloads them. Supports both HTTP API and CLI modes in a single, clean application.

## Features

✅ **Unified Application** - Single script for both CLI and HTTP server modes  
✅ **Direct Readarr Integration** - Works as custom script or HTTP endpoint  
✅ **Automatic Conversion** - MP3 → M4B with proper chapters  
✅ **Smart Chapter Detection** - Uses filenames and silence detection  
✅ **Configurable** - YAML configuration for all settings  
✅ **Container Ready** - Docker support with clean architecture  
✅ **Tested** - Comprehensive test suite included  

## Quick Start

### 1. Installation

```bash
git clone https://github.com/aronjanosch/readarr-m4b-tool.git
cd readarr-m4b-tool
pip install -r requirements.txt
```

### 2. Configuration

Edit `config/config.yaml`:
```yaml
paths:
  audiobooks: "/path/to/your/audiobooks"  # Update this path
```

### 3. Usage Modes

**HTTP Server Mode (Recommended for containers):**
```bash
python src/main.py --server    # or just: python src/main.py
```

**CLI Mode:**
```bash
# Convert specific audiobook
python src/main.py --convert "/path/to/audiobook"

# Test configuration
python src/main.py --test

# Called by Readarr (uses environment variables)
python src/main.py
```

### 4. Readarr Setup

**Option A: Direct CLI (Simple)**
- **Path**: `/path/to/readarr-m4b-tool/src/main.py`
- **Arguments**: *(leave empty)*

**Option B: HTTP API (Container-friendly)**
- Run: `python src/main.py --server`
- Use wrapper script: `scripts/readarr-wrapper.sh`

## Container Setup

**Quick Docker deployment:**

```bash
# 1. Update config and docker-compose.yml paths
# 2. Start container
docker-compose up -d

# 3. Copy wrapper script to Readarr
cp scripts/readarr-wrapper.sh /opt/script/readarr/
```

📖 **[Complete Container Setup Guide](SETUP_GUIDE.md)**

## Testing

Run the test suite:
```bash
python tests/run_tests.py
```

Or run individual tests:
```bash
python tests/test_main.py
python tests/test_config.py
python tests/test_utils.py
```

## Configuration

All settings in `config/config.yaml`:

```yaml
paths:
  audiobooks: "/data/audiobooks"
  temp_dir: "/tmp/readarr-m4b"

conversion:
  audio_codec: "libfdk_aac"
  jobs: 4
  use_filenames_as_chapters: true
  stability_wait_seconds: 30
  cleanup_originals: true

logging:
  level: "INFO"
  file: "./readarr-m4b.log"
```

## Requirements

- **Python 3.11+**
- **[m4b-tool](https://github.com/sandreas/m4b-tool)** - The core conversion engine
- **ffmpeg** - Audio processing (required by m4b-tool)

## Troubleshooting

### Check Logs
```bash
tail -f readarr-m4b.log
```

### Test HTTP API
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"author_name":"Test","book_title":"Test","event_type":"Test"}'
```

### Common Issues

**"Configuration is invalid"**
- Check audiobooks path exists and is writable
- Run: `python src/main.py --test`

**"m4b-tool not found"**
- Install m4b-tool and ensure it's in PATH

**"Permission denied"**
- Make script executable: `chmod +x src/main.py`

## Project Structure

```
readarr-m4b-tool/
├── src/
│   ├── main.py          # Unified CLI + HTTP server
│   ├── config.py        # Configuration management
│   ├── converter.py     # M4B conversion logic
│   └── utils.py         # Utilities
├── tests/               # Test suite
├── scripts/             # Helper scripts
├── config/              # Configuration files
├── Dockerfile           # Container image
└── docker-compose.yml   # Container orchestration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [m4b-tool](https://github.com/sandreas/m4b-tool) - The excellent audiobook conversion engine
- [Readarr](https://github.com/Readarr/Readarr) - Audiobook collection manager 