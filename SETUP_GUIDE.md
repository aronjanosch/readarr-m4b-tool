# ReadarrM4B Container Setup Guide

## 🏗️ **Architecture Overview**

This solution uses a **clean container architecture** that doesn't pollute your Readarr container:

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Readarr   │───▶│  Wrapper Script  │───▶│  ReadarrM4B     │
│ Container   │    │  (tiny bash)     │    │  Container      │
└─────────────┘    └──────────────────┘    └─────────────────┘
                                            │ HTTP Server     │
                                            │ Python          │
                                            │ m4b-tool        │
                                            │ ffmpeg          │
                                            └─────────────────┘
```

## 🚀 **Quick Setup**

### 1. **Deploy ReadarrM4B Container**

```bash
# Clone the repository
git clone https://github.com/yourusername/readarr-m4b-tool.git
cd readarr-m4b-tool

# Edit configuration
nano config/config.yaml

# Update docker-compose volumes
nano docker/docker-compose.yml

# Start the container
cd docker
docker-compose up -d
```

### 2. **Configure Paths**

Edit `config/config.yaml`:
```yaml
paths:
  # This should match your Readarr audiobooks path
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

### 3. **Update Docker Compose Volumes**

Edit `docker/docker-compose.yml`:
```yaml
volumes:
  # Update this path to match your Readarr audiobooks volume
  - /your/actual/audiobooks/path:/data/audiobooks
  # Logs directory
  - ./logs:/var/log
```

### 4. **Place Wrapper Script**

Copy the wrapper script to your Readarr scripts folder:

```bash
# Copy wrapper script to your Readarr scripts folder
cp scripts/readarr-wrapper.sh /opt/script/readarr/

# Make it executable
chmod +x /opt/script/readarr/readarr-wrapper.sh
```

### 5. **Configure Readarr**

In Readarr: **Settings → Connect → Add Custom Script**

- **Name**: ReadarrM4B
- **Path**: `/scripts/readarr/readarr-wrapper.sh` (or your script path)
- **Arguments**: *(leave empty)*
- **Triggers**: ✅ On Import

### 6. **Test Setup**

```bash
# Check if ReadarrM4B container is running
docker ps | grep readarr-m4b

# Test the webhook server
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"author_name":"Test Author","book_title":"Test Book","event_type":"Test"}'

# Test from Readarr (click "Test" button)
```

## 📁 **Directory Structure**

```
/opt/script/readarr/
└── readarr-wrapper.sh     # Tiny wrapper script (only dependency: curl)

/your/audiobooks/path/     # Shared between Readarr and ReadarrM4B
├── Author 1/
│   └── Book 1/
└── Author 2/
    └── Book 2/
```

## 🔧 **Advanced Configuration**

### **Custom Docker Network**

If your Readarr container uses a custom network:

```yaml
# docker-compose.yml
networks:
  readarr_network:
    external: true

services:
  readarr-m4b:
    # ... other config
    networks:
      - readarr_network
```

### **Custom Webhook URL**

If you need a different URL (e.g., different port or host):

Edit `scripts/readarr-wrapper.sh`:
```bash
# Change this line
READARR_M4B_URL="http://your-custom-host:8080"
```

### **Environment Variables**

You can override config via environment variables:

```yaml
# docker-compose.yml
environment:
  - PYTHONUNBUFFERED=1
  - WEBHOOK_PORT=8080
  - READARR_M4B_AUDIOBOOKS_PATH=/data/audiobooks
```

## 🐛 **Troubleshooting**

### **Check Container Status**
```bash
docker ps | grep readarr-m4b
docker logs readarr-m4b
```

### **Check Webhook Server**
```bash
curl -I http://localhost:8080
```

### **Check Logs**
```bash
# ReadarrM4B logs
docker logs readarr-m4b

# Or check log file
tail -f docker/logs/readarr-m4b.log
```

### **Test Wrapper Script**
```bash
# Test the wrapper script manually
export readarr_author_name="Test Author"
export readarr_book_title="Test Book"
export readarr_eventtype="Test"

# Run the wrapper
/opt/script/readarr/readarr-wrapper.sh
```

### **Common Issues**

**"Connection refused"**
- Check if ReadarrM4B container is running
- Verify port 8080 is accessible
- Check if containers are on the same network

**"Audiobooks directory does not exist"**
- Ensure volume mounts match between Readarr and ReadarrM4B
- Check paths in `config/config.yaml`

**"curl: command not found"**
- Install curl in your Readarr container: `apt-get update && apt-get install -y curl`

## ✅ **Benefits of This Architecture**

- ✅ **No dependencies in Readarr** - Just a tiny bash script
- ✅ **Survives Readarr updates** - Nothing installed in Readarr container
- ✅ **Isolated processing** - All heavy lifting in dedicated container
- ✅ **Easy to maintain** - Update ReadarrM4B container independently
- ✅ **Robust communication** - HTTP API instead of file watching
- ✅ **Scalable** - Can handle multiple simultaneous conversions

## 🔄 **Updating ReadarrM4B**

```bash
# Pull latest code
git pull origin main

# Rebuild and restart container
cd docker
docker-compose down
docker-compose up -d --build
```

The wrapper script rarely needs updates, so your Readarr setup remains stable! 