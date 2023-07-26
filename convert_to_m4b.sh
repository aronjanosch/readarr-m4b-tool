#!/bin/bash
WATCH_DIR='/mnt/data/Downloads/audiobooks/files'

# Function to process files
process_files() {
    JSON_FILE="$1"
    JSON_CONTENT=$(cat "$JSON_FILE")
    AUTHOR_NAME=$(echo $JSON_CONTENT | jq -r '.author_name')
    BOOK_TITLE=$(echo $JSON_CONTENT | jq -r '.book_title')
    # Replace colon with space-dash-space in the book title
    BOOK_TITLE=$(echo "$BOOK_TITLE" | sed 's/\([^ ]\):\([^ ]\)/\1 - \2/g; s/\([^ ]\): /\1 - /g')
    INPUT_PATH="/mnt/data/Media/Audiobooks/$AUTHOR_NAME/$BOOK_TITLE"
    OUTPUT_FILE="${AUTHOR_NAME} - ${BOOK_TITLE}.m4b"

    if [ ! -d "$INPUT_PATH" ]; then
        echo "Error: The input directory does not exist."
        exit 1
    fi

    echo "Input path: $INPUT_PATH"

    # Check if there are any .m4b files in the input directory
    if ls "${INPUT_PATH}"/*.m4b 1> /dev/null 2>&1; then
        echo "m4b file(s) already exists, skipping conversion."
        rm $JSON_FILE
        exit 0
    fi

    # Wait for a period of inactivity before processing
    while true; do
        # Wait for changes in the directory for 30 seconds
        if inotifywait -q -e modify -t 30 "$INPUT_PATH" > /dev/null; then
            echo "Detected changes, waiting for them to finish..."
        else
            echo "No changes detected for 30 seconds, proceeding with processing..."
            # Run the m4b-tool command
            cd "$INPUT_PATH"
            m4b-tool.sh merge "." --output-file="$OUTPUT_FILE" -n -v --skip-cover --use-filenames-as-chapters --no-chapter-reindexing --audio-codec=libfdk_aac --jobs="4"

            # Check if the m4b file was created
            if ls "${INPUT_PATH}"/*.m4b 1> /dev/null 2>&1; then
                # Remove all .mp3 files
                rm "${INPUT_PATH}"/*.mp3
                echo "m4b conversion done. Removed original mp3 files."
                rm $JSON_FILE
            else
                echo "Error: m4b file was not created"
            fi
            break
        fi
    done
}

# Wait for a new JSON file to be created
inotifywait -m $WATCH_DIR -e create -e moved_to |
    while read path action file; do
        if [[ "$file" =~ \.json$ ]]; then
            echo "$file detected. Waiting for all files to be copied..."
            process_files "${path}${file}"
        fi
    done