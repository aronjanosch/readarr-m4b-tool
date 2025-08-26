# ReadarrM4B

Simple webhook server that automatically converts audiobook chapters to M4B format when Readarr imports them.

## Requirements

- Python 3.11+
- ffmpeg
- m4b-tool

Check if tools are available:
```bash
ffmpeg -version
m4b-tool --version
```

## Installation

```bash
git clone https://github.com/aronjanosch/readarr-m4b-tool.git
cd readarr-m4b-tool
pip install -r requirements.txt
```

## Configuration

Edit `config/config.yaml`:

```yaml
paths:
  audiobooks: "/path/to/your/audiobooks"  # Must match Readarr's root folder
  temp_dir: "/tmp/readarr-m4b"

conversion:
  audio_codec: "libfdk_aac"
  jobs: 4
  use_filenames_as_chapters: true
  stability_wait_seconds: 30
  cleanup_originals: true  # Remove MP3s after conversion

logging:
  level: "INFO"
  file: "./readarr-m4b.log"

webhook:
  port: 8080
  host: "0.0.0.0"
```

Test configuration:
```bash
python src/main.py --test
```

## Usage

### 1. Start the server

```bash
python src/main.py
```

The server will start on the configured port (default: 8080).

### 2. Configure Readarr webhook

In Readarr:
- Go to Settings → Connect → Add → Webhook
- **URL**: `http://your-server:8080`
- **Method**: POST
- **Triggers**: Enable "On Import"

### 3. That's it!

When Readarr imports an audiobook, it will send a webhook to your server, which will:
1. Wait for files to stabilize
2. Convert MP3 chapters to a single M4B file
3. Optionally clean up the original MP3 files

## Manual conversion

Convert a specific audiobook folder:
```bash
python src/main.py --convert "/path/to/Author/Book Title"
```

## How it works

1. Readarr imports audiobook → sends webhook
2. Server receives webhook with author/book info
3. Finds the audiobook directory using the webhook data
4. Waits for file stability (download complete)
5. Runs `m4b-tool merge` to create single M4B file
6. Optionally removes original MP3 files

## Container setup

If Readarr runs in a container, make sure:
- The webhook URL points to your host machine
- Both Readarr and this tool can access the same audiobook directory
- Use host networking or proper port mapping

## Troubleshooting

**Configuration issues**: Run `python src/main.py --test`

**m4b-tool not found**: Install m4b-tool and ensure it's in PATH

**Permission issues**: Ensure write access to audiobook directory and log file

**Check logs**:
```bash
tail -f readarr-m4b.log
```

## License

MIT License