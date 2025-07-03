FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install m4b-tool
RUN curl -L https://github.com/sandreas/m4b-tool/releases/latest/download/m4b-tool.tar.gz | tar -xzC /tmp \
    && chmod +x /tmp/m4b-tool.phar \
    && mv /tmp/m4b-tool.phar /usr/local/bin/m4b-tool

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Create directories
RUN mkdir -p /var/log /tmp/readarr-m4b

# Make main script executable
RUN chmod +x /app/src/main.py

# Create entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 