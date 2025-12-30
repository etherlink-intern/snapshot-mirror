#!/usr/bin/env python3
"""Snapshot Mirror for Etherlink blockchain data from Nomadic Labs."""

import os
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import time

BASE_URL = "https://snapshotter-sandbox.nomadic-labs.eu/"
NETWORKS = ["etherlink-mainnet", "etherlink-testnet", "etherlink-shadownet"]
TYPES = ["rolling", "full", "archive"]

# Request timeout in seconds
REQUEST_TIMEOUT = 30


def get_block_height(filename):
    """Extract block height from filename pattern: {network}-{type}-{block}.gz"""
    try:
        return int(filename.split('-')[-1].split('.')[0])
    except (ValueError, IndexError):
        return 0


def get_latest_file_info(network, snapshot_type):
    """Fetch the latest snapshot filename for a given network and type."""
    url = f"{BASE_URL}{network}/{snapshot_type}/"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
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
    
    files.sort(key=get_block_height, reverse=True)
    return files[0]


def download_file(url, local_path, dry_run=False):
    """Download a file with .partial suffix to prevent corrupt files on interruption."""
    partial_path = local_path + ".partial"
    
    if dry_run:
        print(f"  [DRY RUN] Would download: {url} -> {local_path}")
        return True
    
    print(f"  Downloading: {url}...")
    try:
        with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(partial_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        print(f"\r  Progress: {pct:.1f}%", end="", flush=True)
            
            print()  # Newline after progress
        
        # Rename .partial to final path only on successful completion
        os.rename(partial_path, local_path)
        print(f"  Download complete: {os.path.basename(local_path)}")
        return True
    
    except Exception as e:
        print(f"\n  Download failed: {e}")
        # Clean up partial file on failure
        if os.path.exists(partial_path):
            os.remove(partial_path)
        return False


def sync_category(network, snapshot_type, target_dir, dry_run=False, keep_count=1):
    """Sync the latest snapshot for a specific network and type."""
    category_dir = os.path.join(target_dir, network, snapshot_type)
    print(f"[{network}/{snapshot_type}]")
    
    if not dry_run and not os.path.exists(category_dir):
        os.makedirs(category_dir, exist_ok=True)
    
    latest_filename = get_latest_file_info(network, snapshot_type)
    if not latest_filename:
        print(f"  No files found on remote.")
        return True  # Not a failure, just nothing to sync

    latest_url = f"{BASE_URL}{network}/{snapshot_type}/{latest_filename}"
    local_path = os.path.join(category_dir, latest_filename)

    # Check if already downloaded
    if os.path.exists(local_path):
        print(f"  Latest file already exists: {latest_filename}")
    else:
        success = download_file(latest_url, local_path, dry_run)
        if not success and not dry_run:
            return False

    # Retention logic - remove old snapshots
    if os.path.exists(category_dir):
        local_files = [
            f for f in os.listdir(category_dir) 
            if f.startswith(f"{network}-{snapshot_type}-") 
            and f.endswith(".gz") 
            and not f.endswith(".partial")
        ]
        local_files.sort(key=get_block_height, reverse=True)
        
        if len(local_files) > keep_count:
            to_delete = local_files[keep_count:]
            for f in to_delete:
                path = os.path.join(category_dir, f)
                if dry_run:
                    print(f"  [DRY RUN] Would remove old snapshot: {f}")
                else:
                    print(f"  Removing old snapshot: {f}")
                    os.remove(path)
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Mirror Etherlink snapshots.")
    parser.add_argument("--target", default="./snapshots", help="Target directory for snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run")
    parser.add_argument("--keep", type=int, default=1, help="Number of recent snapshots to keep per category")
    parser.add_argument("--networks", nargs="+", default=NETWORKS, help="Networks to sync")
    parser.add_argument("--types", nargs="+", default=TYPES, help="Types to sync")
    
    args = parser.parse_args()

    print(f"=== Snapshot Mirror ===")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Target: {args.target}")
    print(f"Retention: {args.keep} per category")
    print()
    
    all_success = True
    for network in args.networks:
        for snapshot_type in args.types:
            success = sync_category(
                network, snapshot_type, args.target, 
                dry_run=args.dry_run, keep_count=args.keep
            )
            if not success:
                all_success = False
    
    if not all_success:
        print("\nSome syncs failed.")
        sys.exit(1)
    
    print("\nAll syncs completed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
