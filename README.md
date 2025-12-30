# Etherlink Snapshot Mirror (SB-TZAPAC)

A robust, Dockerized mirroring system for Etherlink blockchain snapshots. This tool automatically downloads the latest snapshots from Nomadic Labs and maintains a rolling backup on your Synology NAS.

## ✨ Key Features

- **Smart Versioning**: Automatically extracts block heights from the website to name files correctly.
- **Fail-Safe Fallback**: If versioned links on the server are broken (404), it automatically falls back to the `latest.gz` link while preserving the correct version name.
- **Automatic Retention**: Keeps a configurable number of snapshots (e.g., N and N-1) and deletes older ones to save space.
- **Synology Optimized**: Built for AMD64 architecture with SMB/CIFS volume support and non-root security.
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
Copy `.env.example` to `.env` and fill in your Synology details:
```bash
cp .env.example .env
```
Key variables:
- `SYNOLOGY_IP`: Your NAS local IP.
- `SHARE_NAME`: The shared folder name (e.g., `home`).
- `KEEP_COUNT`: Number of versions to keep (Set to `2` for N and N-1).

### 2. Build & Export the Image
Run the provided build script on your Mac to create a compatible image for Synology:
```bash
./build_image.sh
```
This creates a `snapshot-mirror.tar` file.

### 3. Deploy to Synology
1. **Import Image**: Open **Container Manager** -> **Image** -> **Import** -> Select `snapshot-mirror.tar`.
2. **Setup Folder**: Create a folder in File Station (e.g., `/docker/snapshot-mirror/`) and upload your `docker-compose.yml` and `.env` files there.
3. **Launch Project**: In **Container Manager** -> **Project** -> **Create**, select the folder and use the existing `docker-compose.yml`.

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
1. Re-run `./build_image.sh` on your Mac.
2. Re-import the `.tar` into Synology (you may need to delete the old image first).
3. In Container Manager, **Stop** the project and click **Action** -> **Clean** (or just delete and recreate the project).

### Changing Configurations
To change the sync interval or retention count:
1. Edit the `.env` file directly on your Synology using **Text Editor**.
2. **Restart** the project/container in Container Manager.

### Troubleshooting
- **Logs**: Check the logs in Container Manager to see download progress.
- **Permissions**: Ensure the user `appuser` (UID 1000) has read/write permissions to the Synology share.
- **Exec Format Error**: If you see this, the image was built without the `--platform linux/amd64` flag (Ensure you are using the latest `build_image.sh`).

---

## 📁 Project Structure

- `sync_snapshots.py`: The core Python logic for scraping and downloading.
- `Dockerfile`: Container configuration (hardened for security).
- `docker-compose.yml`: Orchestration for deployment.
- `build_image.sh`: Mac automation script for building/exporting.
- `.env`: Your local secrets and settings.
