FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cifs-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user with UID 1000 to match Synology SMB mount defaults
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g 1000 -r -m appuser

# Copy requirements and script
COPY sync_snapshots.py .

# Install Python dependencies
RUN pip install requests beautifulsoup4

# Environment variables
ENV TARGET_DIR="/snapshots"
ENV KEEP_COUNT=1
ENV SYNC_INTERVAL="3600"

# Create target directory and set ownership
RUN mkdir -p /snapshots && chown -R appuser:appuser /app /snapshots

# Health check to verify connectivity
HEALTHCHECK --interval=300s --timeout=30s --start-period=10s --retries=3 \
  CMD python3 -c "import requests; requests.get('https://snapshotter-sandbox.nomadic-labs.eu/', timeout=10)" || exit 1

# Switch to non-root user
USER appuser

# Loop with backoff on failure
CMD while true; do \
      if python3 sync_snapshots.py --target "$TARGET_DIR" --keep "$KEEP_COUNT"; then \
        echo "Sync completed successfully. Sleeping for $SYNC_INTERVAL seconds..."; \
        sleep "$SYNC_INTERVAL"; \
      else \
        echo "Sync failed. Retrying in 60 seconds..."; \
        sleep 60; \
      fi; \
    done
