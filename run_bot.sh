#!/bin/bash

# Navigate to working directory
cd "$(dirname "$0")"

LAST_RUN_FILE="last_run.txt"
TODAY=$(date +%Y-%m-%d)
CURRENT_HOUR=$(date +%-H)

# 1. If earlier than 8 AM — exit silently
if [ "$CURRENT_HOUR" -lt 8 ]; then
    exit 0
fi

# 2. If already executed today — exit silently
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE")
    if [ "$LAST_RUN" == "$TODAY" ]; then
        exit 0
    fi
fi

# 3. Run publication script using virtual environment
./venv/bin/python main.py

# 4. Save date only after successful execution
if [ $? -eq 0 ]; then
    echo "$TODAY" > "$LAST_RUN_FILE"
fi