# ReadarrM4B

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unified audiobook converter for Readarr: automatically merges MP3 chapters into a single M4B file with proper chapters when books are imported into Readarr. Works both as a direct CLI script (Custom Script in Readarr) and as a small HTTP server.

## Requirements

- Python 3.11+
- ffmpeg
- m4b-tool (uses ffmpeg; provides the merge/chapters engine)

Verify tools are in your PATH:

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

Optional but recommended (virtualenv):

```bash
python3.11 -m venv ~/.venvs/readarr-m4b
~/.venvs/readarr-m4b/bin/pip install -U pip
~/.venvs/readarr-m4b/bin/pip install -r requirements.txt
```

## Configuration

All settings are in `config/config.yaml`.

Minimal setup:

```yaml
paths:
  audiobooks: "/path/to/your/audiobooks"  # Must match where Readarr imports final books
  temp_dir: "/tmp/readarr-m4b"

conversion:
  audio_codec: "libfdk_aac"
  jobs: 4
  use_filenames_as_chapters: true
  no_chapter_reindexing: true
  stability_wait_seconds: 30
  cleanup_originals: true

logging:
  level: "INFO"
  file: "./readarr-m4b.log"
```

Quick validation:

```bash
python src/main.py --test
# or
~/.venvs/readarr-m4b/bin/python src/main.py --test
```

## What it does (overview)

- Watches nothing by itself. It converts only when invoked (by Readarr or by you).
- Given a book directory containing MP3 files, it waits for files to stabilize and runs `m4b-tool merge` to produce a single `.m4b` file.
- Output file name is derived from Readarr metadata (Author - Title.m4b) when available, else the directory name.
- Optionally deletes original MP3s after a successful conversion (`cleanup_originals`).

Core components:
- `src/main.py`: unified entrypoint. CLI mode and HTTP server mode.
- `src/config.py`: loads/validates YAML config and builds m4b-tool args.
- `src/converter.py`: conversion workflow (stability checks, merge, cleanup).
- `src/utils.py`: logging setup and small helpers.

## Usage

### CLI mode (manual or Readarr Custom Script)

- Convert a specific book folder:

```bash
python src/main.py --convert "/path/to/Author/Book Title"
```

- Validate configuration only:

```bash
python src/main.py --test
```

- Readarr-triggered (no args): environment variables from Readarr are consumed automatically:

```bash
python src/main.py
```

### HTTP server mode (for webhook-style integration)

Start the server (defaults to port 8080):

```bash
python src/main.py --server
# or simply: python src/main.py
```

Test the endpoint:

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"author_name":"Test Author","book_title":"Test Book","event_type":"Test"}'
```

The server builds the path as `paths.audiobooks/author_name/book_title` and queues conversion.

## Connect to Readarr

You can integrate in two ways. Most users should start with Direct CLI (simplest). If Readarr runs in a container and you want to keep this tool separate, use the HTTP option with a tiny wrapper.

### Option A: Direct CLI (Simple)

Readarr → Settings → Connect → Add → Custom Script
- Name: ReadarrM4B
- Path: full path to Python (e.g. `/usr/bin/python3` or `~/.venvs/readarr-m4b/bin/python`)
- Arguments: absolute path to `src/main.py` (e.g. `/home/you/readarr-m4b-tool/src/main.py`)
- Triggers: enable “On Import” (and any others you prefer)

Notes:
- Ensure `config.paths.audiobooks` matches your Readarr final library path.
- Ensure the Readarr user can write to the audiobooks folder and the log file path.

### Option B: HTTP API (Container-friendly)

- Run the server:

```bash
export WEBHOOK_PORT=8080
python src/main.py --server
```

- Configure Readarr to call a wrapper that POSTs to the server (see `scripts/readarr-wrapper.sh`). Edit the URL inside the script if needed (host/port).

- In Readarr, add a Custom Script pointing to your wrapper script and enable the desired triggers.

## End-to-end flow

1) Readarr imports a book and calls the script (or posts to the HTTP server).
2) The tool locates the book directory under `paths.audiobooks` using author/title.
3) It waits for files to stabilize, then runs m4b-tool to produce `Author - Title.m4b`.
4) Optionally removes the original MP3 files.

Equivalent m4b-tool command:

```bash
m4b-tool merge \
  "/path/to/Author/Book Title" \
  --output-file "/path/to/Author/Book Title/Author - Book Title.m4b" \
  --audio-codec libfdk_aac --jobs 4 -n -v \
  --use-filenames-as-chapters --no-chapter-reindexing
```

## Testing

Run the full test suite:

```bash
python tests/run_tests.py
```

Or individual tests:

```bash
python tests/test_main.py
python tests/test_config.py
python tests/test_utils.py
```

## Troubleshooting

- Configuration invalid:
  - Confirm `paths.audiobooks` exists and is writable.
  - Run `python src/main.py --test` and check output.
- `m4b-tool not found`:
  - Install `m4b-tool` and ensure it is in PATH for the same user running the script.
- Permission denied:
  - Ensure the Readarr user and this tool have permission to read/write the audiobooks directory and the log file path.
- Logs:

```bash
tail -f ./readarr-m4b.log
```

## Project Structure

```
readarr-m4b-tool/
├── src/
│   ├── main.py          # Unified CLI + HTTP server
│   ├── config.py        # Configuration management
│   ├── converter.py     # M4B conversion logic
│   └── utils.py         # Utilities
├── tests/               # Test suite
├── scripts/             # Helper scripts (e.g., Readarr wrapper)
├── config/              # Configuration files
├── Dockerfile           # Container image
└── docker-compose.yml   # Container orchestration
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [m4b-tool](https://github.com/sandreas/m4b-tool) — audiobook conversion engine
- [Readarr](https://github.com/Readarr/Readarr) — audiobook collection manager 