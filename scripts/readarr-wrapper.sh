#!/bin/bash

# ReadarrM4B Wrapper Script
# This tiny script runs in Readarr container and calls the ReadarrM4B container via HTTP
# No dependencies needed - just bash and curl!

# ReadarrM4B service URL (adjust if needed)
READARR_M4B_URL="http://readarr-m4b:8080"

# Build JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
    "author_name": "${readarr_author_name}",
    "book_title": "${readarr_book_title}",
    "author_path": "${readarr_author_path}",
    "event_type": "${readarr_eventtype}"
}
EOF
)

# Send HTTP request to ReadarrM4B container
echo "Sending conversion request to ReadarrM4B..."
echo "Author: ${readarr_author_name}"
echo "Book: ${readarr_book_title}"

# Use curl to send the request
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    "$READARR_M4B_URL" 2>/dev/null)

# Extract HTTP status code
http_code="${response: -3}"
response_body="${response%???}"

# Check if request was successful
if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 202 ]; then
    echo "✅ Conversion request accepted"
    echo "Response: $response_body"
    exit 0
else
    echo "❌ Conversion request failed (HTTP $http_code)"
    echo "Response: $response_body"
    exit 1
fi 