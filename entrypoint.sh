#!/bin/bash

# Default to HTTP server mode if no arguments provided
if [ $# -eq 0 ]; then
    exec python /app/src/main.py --server
else
    exec python /app/src/main.py "$@"
fi 