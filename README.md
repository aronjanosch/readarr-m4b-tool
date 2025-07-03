# ReadarrM4B

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Automatic audiobook converter for Readarr**

Seamlessly converts MP3 audiobooks to M4B format with proper chapters when Readarr downloads them. Built as a simple, efficient Python script that integrates directly with Readarr's custom script functionality.

## Features

✅ **Direct Readarr Integration** - Works as a custom script in Readarr  
✅ **Automatic Conversion** - MP3 → M4B with proper chapters  
✅ **Smart Chapter Detection** - Uses filenames and silence detection  
✅ **Configurable** - YAML configuration for all settings  
✅ **Robust Error Handling** - Comprehensive logging and recovery  
✅ **Test Mode Support** - Compatible with Readarr's test function  

## Quick Start

### 1. Installation

```bash
git clone https://github.com/yourusername/readarr-m4b-tool.git
cd readarr-m4b-tool
pip install -r requirements.txt
```

### 2. Configuration

Edit `config/config.yaml` and set your audiobook path:

```yaml
paths:
  audiobooks: "/path/to/your/audiobooks"  # Update this path
```

### 3. Readarr Setup

In Readarr: **Settings → Connect → Add Custom Script**

- **Name**: ReadarrM4B
- **Path**: `/path/to/readarr-m4b-tool/src/main.py`
- **Arguments**: *(leave empty)*
- **Triggers**: ✅ On Import

### 4. Test

Click "Test" in Readarr to verify the setup works.

## How It Works

```
Readarr Download Complete → ReadarrM4B → M4B Conversion → Cleanup
```

1. **Readarr** downloads audiobook (MP3 files)
2. **ReadarrM4B** detects the completion and starts conversion
3. **m4b-tool** merges files with chapter detection
4. **Original MP3s** are cleaned up (configurable)

## Configuration

All settings are in `config/config.yaml`:

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
  file: "/var/log/readarr-m4b.log"
```

## Manual Usage

```bash
# Convert specific audiobook
python src/main.py --convert "/path/to/audiobook"

# Test configuration
python src/main.py --test
```

## Requirements

- **Python 3.11+**
- **[m4b-tool](https://github.com/sandreas/m4b-tool)** - The core conversion engine
- **ffmpeg** - Audio processing (required by m4b-tool)

## Docker Support

```bash
# Build image
docker build -t readarr-m4b .

# Run with docker-compose
docker-compose up -d
```

## Troubleshooting

### Check Logs
```bash
tail -f /var/log/readarr-m4b.log
```

### Common Issues

**"No valid Readarr information found"**
- Ensure the script is triggered by Readarr with proper environment variables

**"m4b-tool not found"**
- Install m4b-tool and ensure it's in your PATH

**"Permission denied"**
- Make sure the script is executable: `chmod +x src/main.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [m4b-tool](https://github.com/sandreas/m4b-tool) - The excellent audiobook conversion engine
- [Readarr](https://github.com/Readarr/Readarr) - Audiobook collection manager 