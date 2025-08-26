# Multi-stage build: m4b-tool dependencies + Python for readarr-m4b-tool
FROM sandreas/ffmpeg:5.0.1-3 as ffmpeg
FROM sandreas/tone:v0.2.5 as tone
FROM sandreas/mp4v2:2.1.1 as mp4v2
FROM sandreas/fdkaac:2.0.1 as fdkaac
FROM python:3.11-alpine

ENV WORKDIR=/mnt/
ENV M4BTOOL_TMP_DIR=/tmp/m4b-tool/
ENV PYTHONUNBUFFERED=1

# Install system dependencies including PHP for m4b-tool
RUN apk add --no-cache --update --upgrade \
    # mp4v2: required libraries
    libstdc++ \
    # m4b-tool: php cli, required extensions and php settings
    php83-cli \
    php83-curl \
    php83-dom \
    php83-xml \
    php83-mbstring \
    php83-openssl \
    php83-phar \
    php83-simplexml \
    php83-tokenizer \
    php83-xmlwriter \
    php83-zip \
    # Additional tools
    wget \
    && echo "date.timezone = UTC" >> /etc/php83/php.ini \
    && ln -s /usr/bin/php83 /bin/php

# Copy m4b-tool dependencies from official images
COPY --from=ffmpeg /usr/local/bin/ff* /usr/local/bin/
COPY --from=tone /usr/local/bin/tone /usr/local/bin/
COPY --from=mp4v2 /usr/local/bin/mp4* /usr/local/bin/
COPY --from=mp4v2 /usr/local/lib/libmp4v2* /usr/local/lib/
COPY --from=fdkaac /usr/local/bin/fdkaac /usr/local/bin/

# Install m4b-tool (use .phar directly instead of tar.gz)
ARG M4B_TOOL_DOWNLOAD_LINK="https://github.com/sandreas/m4b-tool/releases/download/v0.5.2/m4b-tool.phar"
RUN echo "---- INSTALL M4B-TOOL ----" \
    && wget "${M4B_TOOL_DOWNLOAD_LINK}" -O /usr/local/bin/m4b-tool \
    && chmod +x /usr/local/bin/m4b-tool

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

# Expose webhook port
EXPOSE 8080

# Default to server mode
CMD ["python", "/app/src/main.py", "--server"] 