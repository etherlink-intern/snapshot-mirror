# Etherlink Snapshot Mirror (SB-TZAPAC)

A robust, Dockerized mirroring system for Etherlink blockchain snapshots. This tool automatically downloads the latest snapshots from Nomadic Labs and maintains a rolling backup on your NAS or local storage.

## ✨ Key Features

- **Smart Versioning**: Automatically extracts block heights from the website to name files correctly.
- **Fail-Safe Fallback**: If versioned links on the server are broken (404), it automatically falls back to the `latest.gz` link while preserving the correct version name.
- **Automatic Retention**: Keeps a configurable number of snapshots (e.g., N and N-1) and deletes older ones to save space.
- **NAS Optimized**: Built for AMD64 architecture with SMB/CIFS/NFS volume support and non-root security.
- **Resilient**: Uses `.partial` download tracking to ensure no corrupt files are left if a download is interrupted by a restart.

---

## 🔄 Execution Flow

The script automatically iterates through every combination of networks and snapshot types in each sync cycle:

1.  **Iterates Networks**: Mainnet → Testnet → Shadownet.
2.  **Iterates Types**: Rolling → Full → Archive.
3.  **Total Checks**: It performs **9 sync attempts** (3 networks × 3 types) per cycle.

In the logs, it will appear like this:
```text
[etherlink-mainnet/rolling]
  ... checks and downloads ...
[etherlink-mainnet/full]
  ...
[etherlink-mainnet/archive]
  ...
[etherlink-testnet/rolling]
  ... (skips or warns if server has no files)
```

---

## 🚀 Setup & Deployment

### 1. Configure the Environment
Copy `.env.example` to `.env` and fill in your storage details:
```bash
cp .env.example .env
```
Key variables:
- `NAS_IP`: Your NAS or server local IP.
- `SHARE_NAME`: The shared folder name or mount point.
- `KEEP_COUNT`: Number of versions to keep (Set to `2` for N and N-1).

### 2. Build & Export the Image
Run the provided build script on your machine to create a compatible image:
```bash
./build_image.sh
```
This creates a `snapshot-mirror.tar` file.

### 3. Deployment

⚠️ **Docker Compose Files - Important Note**

This repository includes two Docker Compose files:
- **docker-compose.yml**: Public-safe template (no sensitive config).
- **docker-compose.prod.yml**: Production configuration (contains volume auth - gitignored).

For deployment, use `docker-compose.prod.yml` which includes your network storage configuration (CIFS/NFS/etc.).
The public `docker-compose.yml` contains only placeholder comments and requires manual configuration.

---

**General Steps (Example using Synology Container Manager or Portainer):**

1. **Import Image**: Import the `snapshot-mirror.tar` into your container engine.
2. **Setup Folder**: Create a project folder and upload your `docker-compose.prod.yml` and `.env` files.
3. **Launch Project**: Create a new project/stack and use the existing `docker-compose.prod.yml`.

### 4. Check Health Status (Optional)
You can run a quick health check locally to see which snapshots are actually online on the server:
```bash
python3 check_status.py
```
This will show you a table of which listing pages are up, which versioned files are 404ing, and which `latest.gz` aliases are working.

---

## 🛠 Maintenance

### Updating the Image
If you want to pull new code changes or logic updates:
1. Re-run `./build_image.sh`.
2. Re-import the `.tar` into your NAS.
3. In your container manager, **Stop** the project and click **Action** -> **Clean** (or just delete and recreate the project).

### Changing Configurations
To change the sync interval or retention count:
1. Edit the `.env` file directly on your NAS.
2. **Restart** the project/container.

### Troubleshooting
- **Logs**: Check the logs in your container manager to see download progress.
- **Permissions**: Ensure the user `appuser` (UID 1000) has read/write permissions to the shared storage.
- **Exec Format Error**: If you see this, the image was built without the `--platform linux/amd64` flag (Ensure you are using the latest `build_image.sh`).

---

## 📁 Project Structure

- `sync_snapshots.py`: The core Python logic for scraping and downloading.
- `Dockerfile`: Container configuration (hardened for security).
- `docker-compose.prod.yml`: Production orchestration with CIFS volumes (gitignored).
- `docker-compose.yml`: Public-safe template with placeholder comments.
- `build_image.sh`: Mac automation script for building/exporting.
- `.env`: Your local secrets and settings.
