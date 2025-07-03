#!/bin/bash

# Default to readarr mode if no arguments provided
if [ $# -eq 0 ]; then
    exec python /app/src/main.py
else
    exec python /app/src/main.py "$@"
fi 