#!/bin/bash

# Configuration
TARGET_DIR="./snapshots_dry_run"
KEEP_COUNT=1

echo "--- Starting Snapshot Mirror Dry Run ---"
echo "Target Directory: $TARGET_DIR"
echo "Keep Count: $KEEP_COUNT"
echo "---------------------------------------"

# Ensure target directory exists for the script to "see" it (optional for script-only dry run)
# mkdir -p $TARGET_DIR

# Execute the sync script in dry-run mode
python3 sync_snapshots.py --target "$TARGET_DIR" --keep "$KEEP_COUNT" --dry-run

echo "---------------------------------------"
echo "Dry run complete. No files were downloaded or deleted."
