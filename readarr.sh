#!/bin/bash

# Readarr passes information via environment variables
AUTHOR_NAME="$readarr_author_name"
BOOK_TITLE="$readarr_book_title"

# Print out the environment variables for debugging
echo "Author name: ${AUTHOR_NAME}"
echo "Book title: ${BOOK_TITLE}"

# Check if the required environment variables are set
if [ -z "$AUTHOR_NAME" ] || [ -z "$BOOK_TITLE" ]; then
  echo "No information"
  exit 0
fi

# Format the filename by removing special characters and replacing spaces with underscores
SAFE_AUTHOR_NAME=$(echo "$AUTHOR_NAME" | tr -dc '[:alnum:]\n\r' | tr ' ' '_')
SAFE_BOOK_TITLE=$(echo "$BOOK_TITLE" | tr -dc '[:alnum:]\n\r' | tr ' ' '_')
FILENAME="${SAFE_AUTHOR_NAME}_${SAFE_BOOK_TITLE}.json"

# Print out the filename for debugging
echo "Filename: ${FILENAME}"

# Write the data to a JSON file
cat <<EOF > /data/Downloads/audiobooks/files/${FILENAME}
{
    "author_name": "$AUTHOR_NAME",
    "book_title": "$BOOK_TITLE"
}
EOF
