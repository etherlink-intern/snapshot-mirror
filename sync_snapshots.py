import os
import requests
from bs4 import BeautifulSoup
import argparse
import sys
from urllib.parse import urljoin

BASE_URL = "https://snapshotter-sandbox.nomadic-labs.eu/"
NETWORKS = ["etherlink-mainnet", "etherlink-testnet", "etherlink-shadownet"]
TYPES = ["rolling", "full", "archive"]

def get_latest_file_info(network, snapshot_type):
    url = f"{BASE_URL}{network}/{snapshot_type}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    
    files = []
    for link in links:
        href = link.get('href')
        if not href:
            continue
        
        # Look for files matching the pattern network-type-block.gz
        # Example: etherlink-mainnet-rolling-35084466.gz
        if href.startswith(f"{network}-{snapshot_type}-") and href.endswith(".gz") and "latest" not in href:
            files.append(href)
    
    if not files:
        return None
    
    # Sort files by block height (the number at the end)
    # Pattern: {network}-{type}-{block}.gz
    def get_block_height(filename):
        try:
            return int(filename.split('-')[-1].split('.')[0])
        except ValueError:
            return 0
            
    files.sort(key=get_block_height, reverse=True)
    return files[0]

def sync_category(network, snapshot_type, target_dir, dry_run=False, keep_count=1):
    category_dir = os.path.join(target_dir, network, snapshot_type)
    if not dry_run and not os.path.exists(category_dir):
        os.makedirs(category_dir, exist_ok=True)
    
    latest_filename = get_latest_file_info(network, snapshot_type)
    if not latest_filename:
        print(f"[{network}/{snapshot_type}] No files found.")
        return

    latest_url = f"{BASE_URL}{network}/{snapshot_type}/{latest_filename}"
    local_path = os.path.join(category_dir, latest_filename)

    if os.path.exists(local_path):
        print(f"[{network}/{snapshot_type}] Latest file already exists: {latest_filename}")
    else:
        if dry_run:
            print(f"[{network}/{snapshot_type}] [DRY RUN] Would download: {latest_url} -> {local_path}")
        else:
            print(f"[{network}/{snapshot_type}] Downloading: {latest_url}...")
            try:
                with requests.get(latest_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"[{network}/{snapshot_type}] Download complete.")
            except Exception as e:
                print(f"[{network}/{snapshot_type}] Download failed: {e}")

    # Retention logic
    if not dry_run and os.path.exists(category_dir):
        local_files = [f for f in os.listdir(category_dir) if f.startswith(f"{network}-{snapshot_type}-") and f.endswith(".gz")]
        # Re-sort local files by block height
        def get_block_height(filename):
            try:
                return int(filename.split('-')[-1].split('.')[0])
            except ValueError:
                return 0
        local_files.sort(key=get_block_height, reverse=True)
        
        if len(local_files) > keep_count:
            to_delete = local_files[keep_count:]
            for f in to_delete:
                path = os.path.join(category_dir, f)
                print(f"[{network}/{snapshot_type}] Removing old snapshot: {f}")
                os.remove(path)
    elif dry_run:
         # In dry run, we could mock the retention check if the dir exists
         if os.path.exists(category_dir):
            local_files = [f for f in os.listdir(category_dir) if f.startswith(f"{network}-{snapshot_type}-") and f.endswith(".gz")]
            def get_block_height(filename):
                try:
                    return int(filename.split('-')[-1].split('.')[0])
                except ValueError:
                    return 0
            local_files.sort(key=get_block_height, reverse=True)
            if len(local_files) > keep_count:
                to_delete = local_files[keep_count:]
                for f in to_delete:
                    print(f"[{network}/{snapshot_type}] [DRY RUN] Would remove old snapshot: {f}")

def main():
    parser = argparse.ArgumentParser(description="Mirror Etherlink snapshots.")
    parser.add_argument("--target", default="./snapshots", help="Target directory for snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run")
    parser.add_argument("--keep", type=int, default=1, help="Number of recent snapshots to keep per category")
    parser.add_argument("--networks", nargs="+", default=NETWORKS, help="Networks to sync")
    parser.add_argument("--types", nargs="+", default=TYPES, help="Types to sync")
    
    args = parser.parse_args()

    print(f"Starting sync (Dry Run: {args.dry_run}, Keep: {args.keep})")
    
    for network in args.networks:
        for snapshot_type in args.types:
            sync_category(network, snapshot_type, args.target, dry_run=args.dry_run, keep_count=args.keep)

if __name__ == "__main__":
    main()
