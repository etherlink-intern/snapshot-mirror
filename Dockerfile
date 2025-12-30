FROM python:3.11-slim

# Install system dependencies (including cifs-utils for potential manual mounts)
RUN apt-get update && apt-get install -y \
    cifs-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and script
COPY sync_snapshots.py .

# Install Python dependencies
RUN pip install requests beautifulsoup4

# Environment variables
ENV TARGET_DIR="/snapshots"
ENV KEEP_COUNT=1
ENV SYNC_INTERVAL="3600"

# Create target directory
RUN mkdir -p /snapshots

# Simple loop to run the sync script periodically
CMD while true; do \
      python3 sync_snapshots.py --target "$TARGET_DIR" --keep "$KEEP_COUNT"; \
      echo "Sleeping for $SYNC_INTERVAL seconds..."; \
      sleep "$SYNC_INTERVAL"; \
    done
